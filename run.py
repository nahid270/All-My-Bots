import os
import subprocess
import time
import sys
from config import REPO_LIST

# চলমান প্রসেসগুলো এখানে জমা থাকবে
processes = []

def clean_url(url):
    """লিংক থেকে অপ্রয়োজনীয় স্পেস বা স্ল্যাশ ডিলিট করে"""
    return url.strip().rstrip("/")

def parse_env_string(env_string):
    """
    হোস্টিং প্যানেলের স্ট্রিং (যেমন: 'URL=google.com PORT=8080') 
    কে ভেঙে ডিকশনারি বানাবে।
    """
    env_dict = {}
    if not env_string:
        return env_dict
    
    # লাইন ব্রেক বা কমা থাকলে সেটাকে স্পেস বানিয়ে দিচ্ছি
    clean_text = env_string.replace("\n", " ").replace(",", " ")
    
    # স্পেস দিয়ে আলাদা করা
    pairs = clean_text.split()
    for pair in pairs:
        if "=" in pair:
            key, value = pair.split("=", 1)
            env_dict[key] = value
    return env_dict

def deploy_bots():
    print("🚀 --- Starting Advanced Multi-Bot Deployment ---")
    
    # মেইন সার্ভারের বর্তমান এনভায়রনমেন্ট কপি করে নেওয়া
    system_env = os.environ.copy()
    
    for index, bot in enumerate(REPO_LIST):
        serial = index + 1  # ১ থেকে গণনা শুরু
        
        raw_link = bot["link"]
        repo_link = clean_url(raw_link)
        start_file = bot["start_file"]
        
        # লিংক থেকে ফোল্ডারের নাম বের করা
        folder_name = repo_link.split("/")[-1].replace(".git", "")
        
        print(f"\n🔹 [Bot-{serial}] Processing: {folder_name}...")

        # --- ভেরিয়েবল সেটআপ (গুরুত্বপূর্ণ অংশ) ---
        # আমরা খুঁজবো ENV_1, ENV_2 ইত্যাদি নামে কোনো ভেরিয়েবল আছে কিনা
        env_key = f"ENV_{serial}"
        custom_vars_string = os.environ.get(env_key)
        
        # নতুন এনভায়রনমেন্ট তৈরি করা
        bot_specific_env = system_env.copy()
        
        if custom_vars_string:
            print(f"   ✨ Custom Variables Found in '{env_key}'")
            parsed_vars = parse_env_string(custom_vars_string)
            bot_specific_env.update(parsed_vars) # ভেরিয়েবলগুলো যুক্ত করা হলো
            print(f"   👉 Injected Keys: {list(parsed_vars.keys())}")
        else:
            print(f"   ℹ️ No custom variables found for Bot-{serial} (Checked '{env_key}')")

        # ১. ডাউনলোড (Clone)
        if not os.path.exists(folder_name):
            print(f"   ⬇️ Downloading Repo...")
            subprocess.run(["git", "clone", repo_link])
        
        if os.path.exists(folder_name):
            # ২. রিকোয়ারমেন্টস
            req_file = os.path.join(folder_name, "requirements.txt")
            if os.path.exists(req_file):
                print(f"   📦 Installing requirements...")
                subprocess.run([sys.executable, "-m", "pip", "install", "-r", req_file], stdout=subprocess.DEVNULL)
            
            # ৩. মেইন ফাইল চেক
            run_path = os.path.join(folder_name, start_file)
            if not os.path.exists(run_path):
                # অটোমেটিক ফাইল খোঁজার চেষ্টা
                possible_files = ["app.py", "main.py", "bot.py"]
                for f in possible_files:
                    if os.path.exists(os.path.join(folder_name, f)):
                        start_file = f
                        print(f"   ⚠️ Original file missing. Found & Using: {start_file}")
                        break
            
            # ৪. বট রান করা (কাস্টম ভেরিয়েবল সহ)
            print(f"   ✅ Starting Bot-{serial}...")
            try:
                # env=bot_specific_env দেওয়ার ফলে বটটি আপনার কাস্টম ভেরিয়েবল পাবে
                proc = subprocess.Popen([sys.executable, start_file], cwd=folder_name, env=bot_specific_env)
                processes.append(proc)
            except Exception as e:
                print(f"   ❌ Error starting bot: {e}")
        else:
            print(f"   ❌ Error: Folder not found. Git clone failed.")

if __name__ == "__main__":
    deploy_bots()
    print("\n🎉 --- All Bots Deployed & Running ---")
    
    try:
        # প্রোগ্রাম আজীবন চলার জন্য লুপ
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down all bots...")
        for p in processes:
            p.terminate()
