# run.py
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
        
        # ১. গিটহ্যাব থেকে ফোল্ডারের নাম বের করা
        folder_name = repo_link.split("/")[-1].replace(".git", "")
        
        # ২. যদি ফোল্ডার না থাকে, তাহলে ক্লোন (Clone) করবে
        if not os.path.exists(folder_name):
            print(f"[Downloading] {folder_name}...")
            subprocess.run(["git", "clone", repo_link])
        else:
            print(f"[Found] {folder_name} already exists.")

        # ৩. রিকোয়ারমেন্টস (Requirements) ইনস্টল করা
        req_file = os.path.join(folder_name, "requirements.txt")
        if os.path.exists(req_file):
            print(f"[Installing Requirements] for {folder_name}...")
            subprocess.run(["pip", "install", "-r", req_file])
        
        # ৪. বট রান করা (Start Bot)
        run_cmd = f"python {folder_name}/{start_file}"
        print(f"[Starting] {folder_name}...")
        
        # subprocess.Popen ব্যবহার করা হচ্ছে যাতে সব একসাথে চলে
        proc = subprocess.Popen(["python", f"{folder_name}/{start_file}"])
        processes.append(proc)
        print(f"✅ {folder_name} is running!")

if __name__ == "__main__":
    deploy_bots()
    print("--- All Bots Deployed Successfully ---")
    
    # স্ক্রিপ্ট যাতে বন্ধ না হয়, তাই ইনফিনিটি লুপে রাখা হলো
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("Stopping all bots...")
        for p in processes:
            p.terminate()
