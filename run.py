import os
import subprocess
import time
from config import REPO_LIST

processes = []

def deploy_bots():
    print("--- Starting Multi-Bot Deployment ---")
    
    for bot in REPO_LIST:
        repo_link = bot["link"].strip("/") # <--- এই লাইনটি স্ল্যাশ রিমুভ করবে
        start_file = bot["start_file"]
        
        # ফোল্ডারের নাম বের করা
        folder_name = repo_link.split("/")[-1].replace(".git", "")
        
        # ১. ডাউনলোড (Clone)
        if not os.path.exists(folder_name):
            print(f"[Downloading] {folder_name}...")
            subprocess.run(["git", "clone", repo_link])
        
        # ২. ফোল্ডার চেক এবং রান
        if os.path.exists(folder_name):
            # রিকোয়ারমেন্টস
            req_file = os.path.join(folder_name, "requirements.txt")
            if os.path.exists(req_file):
                print(f"[Installing Requirements] for {folder_name}...")
                subprocess.run(["pip", "install", "-r", req_file])
            
            # বট স্টার্ট
            print(f"[Starting] {folder_name}...")
            try:
                # cwd=folder_name এর মানে হলো ওই ফোল্ডারের ভেতরে ঢুকে কাজ করা
                proc = subprocess.Popen(["python", start_file], cwd=folder_name)
                processes.append(proc)
                print(f"✅ {folder_name} is running!")
            except Exception as e:
                print(f"❌ Failed to start {folder_name}: {e}")
        else:
            print(f"❌ Error: Folder '{folder_name}' not found! Check the Git Link.")

if __name__ == "__main__":
    deploy_bots()
    print("--- All Bots Processed ---")
    
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("Stopping all bots...")
        for p in processes:
            p.terminate()
