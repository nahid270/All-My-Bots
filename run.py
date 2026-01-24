import os
import subprocess
import time
import sys
from config import REPO_LIST

# প্রসেসগুলো ট্র্যাক করার জন্য ডিকশনারি
BOT_PROCESSES = {}

def clean_url(url):
    return url.strip().rstrip("/")

def parse_env_string(env_string):
    """হোস্টিং প্যানেলের স্ট্রিং ভেঙে ডিকশনারি বানাবে"""
    env_dict = {}
    if not env_string:
        return env_dict
    
    clean_text = env_string.replace("\n", " ").replace(",", " ")
    pairs = clean_text.split()
    for pair in pairs:
        if "=" in pair:
            key, value = pair.split("=", 1)
            env_dict[key] = value
    return env_dict

def start_bot(index, bot_config):
    """নির্দিষ্ট একটি বট স্টার্ট করার ফাংশন"""
    serial = index + 1
    raw_link = bot_config["link"]
    repo_link = clean_url(raw_link)
    start_file = bot_config["start_file"]
    folder_name = repo_link.split("/")[-1].replace(".git", "")

    print(f"\n🔄 [Supervisor] Checking Bot-{serial}: {folder_name}...")

    # ১. ডাউনলোড (যদি না থাকে)
    if not os.path.exists(folder_name):
        print(f"   ⬇️ Downloading Repo...")
        subprocess.run(["git", "clone", repo_link])
        
        # রিকোয়ারমেন্টস ইনস্টল (প্রথমবার ডাউনলোডের পর)
        req_file = os.path.join(folder_name, "requirements.txt")
        if os.path.exists(req_file):
            print(f"   📦 Installing requirements...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", req_file], stdout=subprocess.DEVNULL)

    # ২. ফাইল চেক
    if os.path.exists(folder_name):
        run_path = os.path.join(folder_name, start_file)
        if not os.path.exists(run_path):
            possible_files = ["app.py", "main.py", "bot.py"]
            for f in possible_files:
                if os.path.exists(os.path.join(folder_name, f)):
                    start_file = f
                    break
        
        # ৩. ভেরিয়েবল সেটআপ (ENV_1, ENV_2...)
        system_env = os.environ.copy()
        env_key = f"ENV_{serial}"
        custom_vars_string = os.environ.get(env_key)
        
        bot_env = system_env.copy()
        if custom_vars_string:
            print(f"   ✨ Loading custom variables from {env_key}")
            parsed_vars = parse_env_string(custom_vars_string)
            bot_env.update(parsed_vars)
        
        # ৪. বট স্টার্ট করা
        print(f"   🚀 Starting Bot-{serial}...")
        try:
            # log output দেখার জন্য stdout/stderr পাইপ করা হলো না, সরাসরি কনসোলে দেখাবে
            proc = subprocess.Popen([sys.executable, start_file], cwd=folder_name, env=bot_env)
            return proc
        except Exception as e:
            print(f"   ❌ Failed to start Bot-{serial}: {e}")
            return None
    else:
        print("   ❌ Error: Repo folder not found.")
        return None

def main_loop():
    print("🚀 --- Multi-Bot Supervisor Started ---")
    
    while True:
        for index, bot in enumerate(REPO_LIST):
            serial = index + 1
            
            # প্রসেস যদি আগে থেকে থাকে
            if serial in BOT_PROCESSES:
                proc = BOT_PROCESSES[serial]
                # poll() রিটার্ন কোড দেয়। None মানে চলছে, অন্য কিছু মানে বন্ধ হয়ে গেছে
                status = proc.poll()
                
                if status is None:
                    # বট দিব্যি চলছে, কিছু করার দরকার নেই
                    continue 
                else:
                    print(f"⚠️ [Alert] Bot-{serial} stopped or crashed! (Exit Code: {status})")
                    print("   🔄 Restarting in 5 seconds...")
                    # প্রসেস লিস্ট থেকে সরিয়ে আবার নতুন করে চালু করা হবে
                    del BOT_PROCESSES[serial]
            
            # বট চালু করা (যদি লিস্টে না থাকে বা ক্র্যাশ করে থাকে)
            new_proc = start_bot(index, bot)
            if new_proc:
                BOT_PROCESSES[serial] = new_proc
        
        # ১০ সেকেন্ড অপেক্ষা করে আবার চেক করবে
        time.sleep(10)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\n🛑 Stopping all bots...")
        for p in BOT_PROCESSES.values():
            p.terminate()
