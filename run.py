import os
import subprocess
import time
from config import REPO_LIST

processes = []

def clean_url(url):
    """লিংক থেকে বাড়তি স্ল্যাশ বা স্পেস রিমুভ করে"""
    return url.strip().rstrip("/")

def deploy_bots():
    print("🚀 --- Starting Smart Multi-Bot Deployment ---")
    
    for bot in REPO_LIST:
        raw_link = bot["link"]
        repo_link = clean_url(raw_link)
        start_file = bot["start_file"]
        
        # লিংক থেকে ফোল্ডারের নাম বের করা
        folder_name = repo_link.split("/")[-1].replace(".git", "")
        
        print(f"\n🔍 Processing: {folder_name}...")

        # ১. ডাউনলোড (Clone) করা
        if not os.path.exists(folder_name):
            print(f"⬇️ Downloading from: {repo_link}")
            result = subprocess.run(["git", "clone", repo_link])
            
            if result.returncode != 0:
                print(f"❌ ERROR: Download Failed! Link or Permission issue.")
                continue # ডাউনলোড না হলে পরের বটে চলে যাবে
        else:
            print(f"📂 Folder '{folder_name}' already exists.")

        # ২. ফোল্ডার চেক করা
        if os.path.exists(folder_name):
            # রিকোয়ারমেন্টস ইনস্টল
            req_file = os.path.join(folder_name, "requirements.txt")
            if os.path.exists(req_file):
                print(f"📦 Installing requirements...")
                subprocess.run(["pip", "install", "-r", req_file], stdout=subprocess.DEVNULL)
            
            # ৩. মেইন ফাইল চেক করা
            run_path = os.path.join(folder_name, start_file)
            if not os.path.exists(run_path):
                print(f"⚠️ Warning: '{start_file}' not found inside '{folder_name}'!")
                # অপশনাল: অটোমেটিক ফাইল খোঁজার চেষ্টা (যদি bot.py না থাকে)
                possible_files = ["app.py", "main.py"]
                for f in possible_files:
                    if os.path.exists(os.path.join(folder_name, f)):
                        print(f"💡 Found '{f}' instead. Using it...")
                        start_file = f
                        break
            
            # ৪. বট রান করা
            print(f"✅ Starting {folder_name} ({start_file})...")
            try:
                proc = subprocess.Popen(["python", start_file], cwd=folder_name)
                processes.append(proc)
            except Exception as e:
                print(f"❌ Failed to start: {e}")
        else:
            print(f"❌ Error: Folder not found after cloning. Check URL.")

if __name__ == "__main__":
    deploy_bots()
    print("\n🎉 --- All Bots Processed. System Running ---")
    
    try:
        # প্রোগ্রাম যাতে বন্ধ না হয়
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n🛑 Stopping all bots...")
        for p in processes:
            p.terminate()
