import io
import os
import shutil
import errno

def move_handler(src, dst, task="moving files"):
    """
    This program used to move a lot of files around, but now it doesn't really, so this function is obsolete. Kept just in case.
    I wanted shutil.move() to have exception handling because my disks are always nearly full. 

    Should return True if shutil.move is successful and False if not.
    """
    # this is supposed to prevent the function from deleting an entire folder or causing a different exception when trying to delete a partially transfered file.
    real_dst = dst
    if os.path.isdir(dst):
        real_dst = os.path.join(dst, os.path.basename(src))
    
    try:
        shutil.move(src, dst)
        return True
    
    except FileNotFoundError:
        print(f"Error: A file went missing. '{src}' does not exist. This happened while we were {task}.")
        return False
    
    except PermissionError:
        print(f"Error: You do not have permission to read the source or write to the destination. Are either in use by another process? This happened while we were {task}.")
        return False
    
    except shutil.Error as e:
        print(f"Error: Shutil error moving {src} to {dst}: {e}. This happened while we were {task}.")
        return False
    
    except OSError as e:
        if e.errno == errno.ENOSPC:
            print("Error: The destination disk is full.")
            try:
                if os.path.exists(real_dst) and os.path.isfile(real_dst):
                    os.remove(real_dst)
                    print(f"Cleaned up a corrupt file from the destination {real_dst}.")
            except OSError:
                print(f"There may still be a parital or corrupted file at the destination {real_dst}.")
        else: 
            print(f"An unexpected OS error occured: {e}. This happened while we were {task}.")
        return False
    
    except Exception as e:
        print(f"Error: Unexpected error while moving files: {e}. This happened while we were {task}.")
        return False