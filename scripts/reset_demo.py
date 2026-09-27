import os
import glob

def reset():
    print("Resetting demo environment state...")
    db_files = ["data/control_plane.db", "data/source.db", "data/target.db"]
    for f in db_files:
        if os.path.exists(f):
            os.remove(f)

    # Clean quarantine
    if os.path.exists("data/quarantine"):
        for q in glob.glob("data/quarantine/*"):
            os.remove(q)

    # Re-seed
    from scripts.seed_demo_data import seed
    seed()
    print("Reset complete.")

if __name__ == "__main__":
    reset()
