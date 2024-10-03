# Table of Contents
- [Table of Contents](#table-of-contents)
- [Project Description](#project-description)
- [Installation](#installation)
  - [Adding Scripts to Path - Windows](#adding-scripts-to-path---windows)
  - [Adding Scripts to Path - Linux / Unix / MacOS](#adding-scripts-to-path---linux--unix--macos)
- [Usage](#usage)
  - [Overall Workflow](#overall-workflow)
  - [Learning How It Works](#learning-how-it-works)
    - [Making Test Files](#making-test-files)
    - [Scanning for Duplicates](#scanning-for-duplicates)
      - [Using stdin](#using-stdin)
        - [Linux/MacOS/Unix Exmample:](#linuxmacosunix-exmample)
        - [Windows Example](#windows-example)
      - [Using path](#using-path)
    - [Reviewing Results](#reviewing-results)
    - [Deleting Duplicates](#deleting-duplicates)
- [Help](#help)
  - [duple scan --help](#duple-scan---help)
  - [duple rm --help](#duple-rm---help)
  - [duple make-test-files --help](#duple-make-test-files---help)
  - [duple hash-stats --help](#duple-hash-stats---help)
  - [duple version --help](#duple-version---help)
  - [duple wherelog --help](#duple-wherelog---help)
  - [duple followlog --help](#duple-followlog---help)
- [Version History](#version-history)
  - [2.1.5 Modified Output, Fixed Typos](#215-modified-output-fixed-typos)
  - [2.1.3 Fixed Bug](#213-fixed-bug)
  - [2.1.0 Adding Logging, Fixed Bugs](#210-adding-logging-fixed-bugs)
  - [2.0.0 Refactored to Add Features](#200-refactored-to-add-features)
  - [1.1.0 Improved Documentation](#110-improved-documentation)
  - [1.0.0 Refactored and Improved Output and Reporting](#100-refactored-and-improved-output-and-reporting)
  - [0.5.0 Improve Data Outputs](#050-improve-data-outputs)
  - [0.4.0 Performance Improvements](#040-performance-improvements)
  - [0.3.0 Added Capability](#030-added-capability)
  - [0.2.0 Added license](#020-added-license)
  - [0.1.1 Misc. Fixes](#011-misc-fixes)
  - [0.1.0 Initial Release](#010-initial-release)
# Project Description
Duple is a small package that will find and remove duplicate files.

Duple will iterate through all files and directories that is given and find duplicate files (files are compared on their contents, byte by byte).  Duple then outputs a file: duple.delete.  The user should review duple.delete and make edits if needed (instructions are in duple.delete).  Once the review is complete and edits made, another duple command will review duple.delete and delete the apporpriate files.
# Installation
It is strongly recommended to use the latest version of duple.

    pip install duple

or if you need to upgrade:

    pip install duple --upgrade


You may need to add the Python Scripts folder on your computer to the PATH.

## Adding Scripts to Path - Windows
Open PowerShell (Start > [search for powershell]) and copy/paste the following text to the command line:

    python3 -c "from duple.info import get_user_scripts_path;get_user_scripts_path()"

Go to Start > [search for 'edit environment variables for your account'] > Users Variables for [user name] > Select Path in top list box > Click Edit...

Once the window pops up, add to the bottom of the list the result from the PowerShell command above
## Adding Scripts to Path - Linux / Unix / MacOS
Open terminal and copy/paste teh following text to the command line:

    python3 -c "from duple.info import USER_SCRIPTS_PATH;print(USER_SCRIPTS_PATH)"
# Usage
## Overall Workflow
First, open the terminal and navigate to the directory you want to analyze for duplicates.  Then, run 'duple scan', which will make two output files: duple.delete.  Review duple.delete to validate how duple determined which files were original and which were duplicates.  Then, run 'duple rm' to remove the files specified in 'duple.delete'.
## Learning How It Works
The following sections walk through an example from start to finish using only built in functions of Duple.
### Making Test Files
First, we'll make some test files to have something to scan for duplicates.  Navigate to a convenient directory and make a test directory:
    
    cd path_to_convenient_directory
    duple make-test-files -pt
    making directories: 100%|██████████████████████████████████████████████████████| 3/3 [00:00<00:00, 1579.78it/s]

    ├── UOotpgGLv
    │   ├── bWFMyHRrutcAxRibDV.txt
    │   └── QYlFjmULSV
    │       ├── QofPgusOsvlmKWVluYkWQgevDBE.txt
    │       └── HAKhBlspwMkTYtVzTkLoENg.txt
    ├── .DS_Store
    ├── PRynXIdIXkAeaIPAQdCoFQSeuzhrK
    │   ├── BppxnezMcePwzdJLfAEF.txt
    │   └── FrADugjjVuGUvsN
    │       ├── OstZgGsAuyRefYrMWybCOMpSEb.txt
    │       └── GhvqDiXptHJvfmDxP.txt
    └── BKniVYZvtcaiXncTCFAXdwZ
        ├── ewrZSzxOnrkA.txt
        └── KXbShU
            ├── TSRNhUlhRSCM.txt
            └── VfHPJNExNzTadfoHAWfpFVEtXlDZ.txt
### Scanning for Duplicates
#### Using stdin
For the example below, we used the option flags:<br>
    -d means use the depth of the path to determine the original, -d means shallowest, -D means deepest<br>
    -c means use accessed time to determine the original, -c means use oldest created time, -C means use newest created time<br>

When using stdin, the user must only pipe files into the duple scan.  The most common way to use stdin would be to use the find command on Linux/MacOS/Unix and the Get-ChildItem command on Windows PowerShell.

##### Linux/MacOS/Unix Exmample:
    
    > find . -type f | duple scan -d -c
    traversing file tree: 7it [00:00, 11810.19it/s]
    hashing files: 100%|███████████████████████████████████████████████████████████| 8/8 [00:00<00:00, 77.75it/s]
    Total Files.............................................................................10
    Ignored Files............................................................................0
    Duplicate Files..........................................................................6
    Duplicate Groups.........................................................................4
    Total Size (duplicates).............................................................2.1 kB
    Total Size (all files)..............................................................9.7 kB
    Hash Algorithm......................................................................sha256
    File System Traversal Time (seconds)...............................................0.00757
    Pre-Processing Files Time (seconds)................................................0.00025
    Hashing Time (seconds).............................................................0.14561
    Total Time (seconds)...............................................................0.15347
    Duple Version........................................................................2.0.0
    Results Written To............................/Users/shout/Desktop/duple_test/duple.delete

    Open the `output summary results` file listed above with a text editor for review
    Once review and changes are complete, run `duple rm`

##### Windows Example

    PS > Get-ChildItem . -File -Recurse | %{$_.FullName} | duple scan -d -c
    traversing file tree: 7it [00:00, 11810.19it/s]
    hashing files: 100%|███████████████████████████████████████████████████████████| 8/8 [00:00<00:00, 77.75it/s]
    Total Files.............................................................................10
    Ignored Files............................................................................0
    Duplicate Files..........................................................................6
    Duplicate Groups.........................................................................4
    Total Size (duplicates).............................................................2.1 kB
    Total Size (all files)..............................................................9.7 kB
    Hash Algorithm......................................................................sha256
    File System Traversal Time (seconds)...............................................0.00757
    Pre-Processing Files Time (seconds)................................................0.00025
    Hashing Time (seconds).............................................................0.14561
    Total Time (seconds)...............................................................0.15347
    Duple Version........................................................................2.0.0
    Results Written To............................/Users/shout/Desktop/duple_test/duple.delete

    Open the `output summary results` file listed above with a text editor for review
    Once review and changes are complete, run `duple rm`
#### Using path
For the example below, we used the option flags:<br>
    -p for path (. = current directory)<br>
    -d means use the depth of the path to determine the original, -d means shallowest, -D means deepest<br>
    -n means use name length to determine the original, -n means use shortest name, -N means use longest name<br>
    
You can use multiple flags to determine the original, both will be applied.  So, in the case below, we use the shallowest depth and the shortest name to determine the original vs the duplicate(s).

    duple scan -p . -d -n
    traversing file tree: 7it [00:00, 11810.19it/s]
    hashing files: 100%|███████████████████████████████████████████████████████████| 8/8 [00:00<00:00, 77.75it/s]
    Total Files.............................................................................10
    Ignored Files............................................................................0
    Duplicate Files..........................................................................6
    Duplicate Groups.........................................................................4
    Total Size (duplicates).............................................................2.1 kB
    Total Size (all files)..............................................................9.7 kB
    Hash Algorithm......................................................................sha256
    File System Traversal Time (seconds)...............................................0.00757
    Pre-Processing Files Time (seconds)................................................0.00025
    Hashing Time (seconds).............................................................0.14561
    Total Time (seconds)...............................................................0.15347
    Duple Version........................................................................2.0.0
    Results Written To............................/Users/shout/Desktop/duple_test/duple.delete

    Open the `output summary results` file listed above with a text editor for review
    Once review and changes are complete, run `duple rm`
### Reviewing Results
<span style="color:red">**ONLY FILES LISTED IN THE 'Duplicate Results' SECTION OF DUPLE.DELETE WILL BE DELETE**<br>
**THE 'Ignored Files in Scan' SECTION IS IGNORED**</span><br>

Open 'duple.delete' to review and edit the results.  The user can change the left most column in duple.delete.  The following line would be deleted:

    DUPLICATE  |  962 Bytes  | /Users/shout/Desktop/duple_test/UOotpgGLv/QYlFjmULSV/QofPgusOsvlmKWVluYkWQgevDBE.txt

If the user changes the 'DUPLICATE' to 'ORIGINAL', see below, the file on that line will not be deleted.

    ORIGINAL   |  962 Bytes  | /Users/shout/Desktop/duple_test/UOotpgGLv/QYlFjmULSV/QofPgusOsvlmKWVluYkWQgevDBE.txt

A sample duple.delete file is below:

        Duple Report Generated on 2024-10-02T20:43:06.590382-04:00, commanded by user: shout
    ------------------------------------------------------------------------------------------
    Summary Statistics:
    Total Files.............................................................................10
    Ignored Files............................................................................2
    Duplicate Files..........................................................................6
    Duplicate Groups.........................................................................2
    Total Size (duplicates).............................................................2.7 kB
    Total Size (all files).............................................................32.6 kB
    Hash Algorithm......................................................................sha256
    File System Traversal Time (seconds)...............................................0.00645
    Pre-Processing Files Time (seconds)................................................0.00050
    Hashing Time (seconds).............................................................0.15670
    Total Time (seconds)...............................................................0.16371
    Duple Version........................................................................2.1.6
    Results Written To............................/Users/shout/Desktop/duple_test/duple.delete

    ------------------------------------------------------------------------------------------
    Inputs (True = minimum, False = Maximum): 
    depth = True
    namelength = True

    ------------------------------------------------------------------------------------------
    Outputs:
    /Users/shout/Desktop/duple_test/duple.delete

    ------------------------------------------------------------------------------------------
    Instructions to User:
    The sections below describe what action duple will take when 'duple rm' is commanded. The first column is the flag that tells duple what to do:
        ORIGINAL   : means duple will take no action for this file, listed only as a reference to the user
        DUPLICATE  : means duple will send this file to the trash can or recycling bin, if able

    ------------------------------------------------------------------------------------------
    Duplicate Results:
    DUPLICATE  |  565 Bytes  | /Users/shout/Desktop/duple_test/CXnVbEhTJHJmDoSR/JABUvTKiElLxxNeNjZh.txt
    DUPLICATE  |  565 Bytes  | /Users/shout/Desktop/duple_test/PvNEOcwjFlmMGOUQFnqfDsJVzkOLi/eBTYszALyJXoealOjGj.txt
    DUPLICATE  |  565 Bytes  | /Users/shout/Desktop/duple_test/PvNEOcwjFlmMGOUQFnqfDsJVzkOLi/MsxAwYDKeBkmUWLRHAsRRJLOA.txt
    DUPLICATE  |  565 Bytes  | /Users/shout/Desktop/duple_test/PvNEOcwjFlmMGOUQFnqfDsJVzkOLi/mOgjQxE/kTGerbYckSIpJmeXTYUlmnLdQ.txt
    ORIGINAL   |  565 Bytes  | /Users/shout/Desktop/duple_test/bLeKJEGLsdYxMNeEmUC/ERYCCCDsbfdYGiIFfh.txt

    ORIGINAL   |  231 Bytes  | /Users/shout/Desktop/duple_test/CXnVbEhTJHJmDoSR/uWlvcHM.txt
    DUPLICATE  |  231 Bytes  | /Users/shout/Desktop/duple_test/CXnVbEhTJHJmDoSR/rbevPzGoLmvGXJwsOuKuWXhbDq/FxUfdtjxeRGN.txt
    DUPLICATE  |  231 Bytes  | /Users/shout/Desktop/duple_test/bLeKJEGLsdYxMNeEmUC/WWwniGsaAkLr.txt


    ------------------------------------------------------------------------------------------
    Ignored Files in Scan:
    IGNORED    |   28.7 kB   |  UNIQUE_FILE_SIZE  | /Users/shout/Desktop/duple_test/.DS_Store
    IGNORED    |  375 Bytes  |  UNIQUE_FILE_SIZE  | /Users/shout/Desktop/duple_test/bLeKJEGLsdYxMNeEmUC/JsmDv/dioMDVyMZTHeaCJPdCSniu.txt
### Deleting Duplicates
After the user has reviewed/edited the 'duple.delete' file, you can run the duple rm command.  This command <span style="color:red">**will delete files**</span> specified in duple.delete as 'DUPLICATE'.

It is recommended to first do a dry run to review the output, the dry run will **not** delete any files.

    > duple rm -dr
    [   0.0%] will delete          4.0 kB   duple.delete
    [   9.1%] will delete        484 Bytes  UOotpgGLv/bWFMyHRrutcAxRibDV.txt
    [  18.2%] will keep            6.1 kB   .DS_Store
    [  27.3%] will delete        962 Bytes  UOotpgGLv/QYlFjmULSV/QofPgusOsvlmKWVluYkWQgevDBE.txt
    [  36.4%] will keep          962 Bytes  PRynXIdIXkAeaIPAQdCoFQSeuzhrK/FrADugjjVuGUvsN/GhvqDiXptHJvfmDxP.txt
    [  45.5%] will delete        109 Bytes  UOotpgGLv/QYlFjmULSV/HAKhBlspwMkTYtVzTkLoENg.txt
    [  54.5%] will keep          109 Bytes  PRynXIdIXkAeaIPAQdCoFQSeuzhrK/BppxnezMcePwzdJLfAEF.txt
    [  63.6%] will delete        109 Bytes  PRynXIdIXkAeaIPAQdCoFQSeuzhrK/FrADugjjVuGUvsN/OstZgGsAuyRefYrMWybCOMpSEb.txt
    [  72.7%] will delete        109 Bytes  BKniVYZvtcaiXncTCFAXdwZ/ewrZSzxOnrkA.txt
    [  81.8%] will delete        352 Bytes  BKniVYZvtcaiXncTCFAXdwZ/KXbShU/TSRNhUlhRSCM.txt
    [  90.9%] will keep          352 Bytes  BKniVYZvtcaiXncTCFAXdwZ/KXbShU/VfHPJNExNzTadfoHAWfpFVEtXlDZ.txt

If this looks good, then we proceed to:

For verbose output, each file is listed in the output as it is being deleted:

    > duple rm -v

If we don't want to see every file, but just a progress bar:

    > duple rm
# Help
The top level help:
    duple
    Usage: duple [OPTIONS] COMMAND [ARGS]...

    Options:
    --help  Show this message and exit.

    Commands:
    followlog        follow the log until user interupts (ctrl-c), (tail -f)
    hash-stats       report hashing times for each available hashing...
    make-test-files  make test files to learn or test with duple
    rm               rm sends all 'duplicate' files specified in...
    scan             Scan recursively computes a hash of each file and puts...
    version          display the current version of duple
    wherelog         print the path to the logs
## duple scan --help
    duple scan --help
    Usage: duple scan [OPTIONS]

    Scan recursively computes a hash of each file and puts the hash into a
    dictionary.  The keys are the hashes of the files, and the values are the
    file paths and metadata.  If an entry has more than 1 file associated, they
    are duplicates.  The original is determined by the flags or options (ex:
    -d).  The duplicates are added to a file called duple.delete.

    Options:
    -p, --path TEXT                 path to look in for duplicates, if this
                                    option is present, paths is ignored
    -in, --paths_file_stdin FILENAME
                                    either a file containing a list of paths to
                                    evaluate or stdin
    -h, --hash TEXT                 the hashalgorithm to use, default = sha256,
                                    allowed alogorithsm: ['blake2b', 'blake2s',
                                    'md5', 'md5-sha1', 'ripemd160', 'sha1',
                                    'sha224', 'sha256', 'sha384', 'sha3_224',
                                    'sha3_256', 'sha3_384', 'sha3_512',
                                    'sha512', 'sha512_224', 'sha512_256', 'sm3']
    -d, --depth_min                 keep the file with the lowest pathway depth
    -D, --depth_max                 keep the file with the highest pathway depth
    -n, --name_min                  keep the file with the shortest name
    -N, --name_max                  keep the file with the longest name
    -c, --created_min               keep the file with the oldest creation date
    -C, --created_max               keep the file with the newest creation date
    -m, --modified_min              keep the file with the oldest modified date
    -M, --modified_max              keep the file with the newest modified, date
    -a, --accessed_min              keep the file with the oldest accessed, date
    -A, --accessed_max              keep the file with the newest accessed, date
    -ncpu, --number_of_cpus INTEGER
                                    maximum number of cpu cores to use
    -ch, --chunksize INTEGER        chunksize to give to workers, minimum of 2
    --help                          Show this message and exit.
## duple rm --help
    duple rm --help
    Usage: duple rm [OPTIONS]

    rm sends all 'duplicate' files specified in duple.delete to the trash folder

    Options:
    -v, --verbose             be more verbose during execution
    -dr, --dry_run            Perform dry run, do everything except deleting
                                files
    -led, --leave_empty_dirs  Do not delete empty directories/folders
    --help                    Show this message and exit.
## duple make-test-files --help
    duple make-test-files --help
    Usage: duple make-test-files [OPTIONS]

    make test files to learn or test with duple

    Options:
    -tp, --test_path PATH           path where the test directories will be
                                    created
    -nd, --number_of_directories INTEGER
                                    number of directories to make for the test
    -nf, --number_of_files INTEGER  number of files to make in each top level
                                    directory, spread across the directories
    -fs, --max_file_size INTEGER    file size to create in bytes
    -pt, --print_tree               print tree with results
    --help                          Show this message and exit.
## duple hash-stats --help
    duple hash-stats --help
    Usage: duple hash-stats [OPTIONS] PATH

    report hashing times for each available hashing algorithm on the specified
    file

    Args:     path (str): path to file to hash

    Options:
    --help  Show this message and exit.
## duple version --help
    duple version --help
    Usage: duple version [OPTIONS]

    display the current version of duple

    Options:
    --help  Show this message and exit.
## duple wherelog --help
    duple wherelog --help
    Usage: duple wherelog [OPTIONS]

    print the path to the logs

    Options:
    --help  Show this message and exit.
## duple followlog --help
    duple followlog --help
    Usage: duple followlog [OPTIONS]

    follow the log until user interupts (ctrl-c), (tail -f)

    Options:
    --help  Show this message and exit.
# Version History
## 2.1.5 Modified Output, Fixed Typos
- [x] changed output duple.delete All Files section to just be the Ignored files and a disposition code for why the file was ignored
- [x] fixed typo in output duple.delete instructions section
- [x] added duple followlog 
## 2.1.3 Fixed Bug
- [x] fixed bug where IGNORED files were added to the duplicate results, amended test to catch this bug in the future
## 2.1.0 Adding Logging, Fixed Bugs
- [x] added logging
- [x] fixed bug where unicode characters in file names would cause error
- [x] fixed performance issue during duple scan
## 2.0.0 Refactored to Add Features
- [x] added support for multiple filters (ex: -d -n)<br>
- [x] added support for accepting stdin for files to search<br>
- [x] added tree view support to make-test-files<br>
## 1.1.0 Improved Documentation
- [x] Improved README for better installation and setup instructions
## 1.0.0 Refactored and Improved Output and Reporting
- [x] refactored code to be easier to follow and more modular<br>
- [x] improved reporting of results to duple.delete and duple.json<br>
- [x] improved duple.json output, adding additional data<br>
- [x] added dry run and verbose flags to duple rm
- [x] added hash-stats to calculate performance times for each available hash<br>
- [x] added make-test-files to make test files for the user to learn how duple works on test data<br>
## 0.5.0 Improve Data Outputs
- [x] added dictionary to duple.json for file stats, now each entry has a key to describe the number<br>
- [x] fixed progress bar for pre-processing directories<br>
- [x] added output file duple.all_files.json with file statistics on all files within the specified path for 'duple scan'<br>
- [x] Improved summary statistics output for 'duple scan'
## 0.4.0 Performance Improvements
- [x] adding multiprocessing, taking advantage of multiple cores<br>
- [x] eliminated files with unique sizes from analysis - files with unique size are not duplicates of another file
## 0.3.0 Added Capability
- [x] added mv function that will move 'duple.delete' paths instead of deleting them
## 0.2.0 Added license
- [x] Added license
## 0.1.1 Misc. Fixes
- [x] Fixed typos in help strings<br>
- [x] Added support for sending duplicates to trash ('duple rm')
## 0.1.0 Initial Release
- [x] This is the initial release of duple