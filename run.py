import os
import subprocess
import time
from config import REPO_LIST

processes = []

def deploy_bots():
    print("--- Starting Multi-Bot Deployment ---")
    
    for bot in REPO_LIST:
        repo_link = bot["link"]
        start_file = bot["start_file"]
        
        # ফোল্ডারের নাম বের করা
        folder_name = repo_link.split("/")[-1].replace(".git", "")
        
        # ১. ক্লোন করা (যদি না থাকে)
        if not os.path.exists(folder_name):
            print(f"[Downloading] {folder_name}...")
            # প্রাইভেট রিপো এড়াতে এখানে পাবলিক লিংক ব্যবহার করবেন
            subprocess.run(["git", "clone", repo_link])
        
        # ২. রিকোয়ারমেন্টস ইনস্টল করা
        req_file = os.path.join(folder_name, "requirements.txt")
        if os.path.exists(req_file):
            print(f"[Installing Requirements] for {folder_name}...")
            subprocess.run(["pip", "install", "-r", req_file])
        
        # ৩. বট রান করা (সঠিক ডিরেক্টরি বা cwd ব্যবহার করে)
        print(f"[Starting] {folder_name}...")
        
        try:
            # গুরুত্ত্বপূর্ণ পরিবর্তন: cwd=folder_name দেওয়া হয়েছে
            # এতে বট মনে করবে সে তার নিজের ফোল্ডারের ভেতরেই আছে
            proc = subprocess.Popen(["python", start_file], cwd=folder_name)
            processes.append(proc)
            print(f"✅ {folder_name} is running!")
        except Exception as e:
            print(f"❌ Failed to start {folder_name}: {e}")

if __name__ == "__main__":
    deploy_bots()
    print("--- All Bots Deployed Successfully ---")
    
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("Stopping all bots...")
        for p in processes:
            p.terminate()
