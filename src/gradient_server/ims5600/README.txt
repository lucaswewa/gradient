----------------------------------------------------------------------

                   ..:::::::::::::::::::::::..            
               .:::::::...              ..:::::::..       
            .:::::.                            .:::::.    
          .:::. .....        .....        ...:::. .::::   
         .::.   .:::.        .:::.     .:::::::::    :::. 
        .::.    .:::.        .:::.    .::::           .::.
        ::.     .:::.        .:::.    .:::.            .::
        ::      .:::.        .:::.     .::::..          ::
        ::      .:::.        .:::.      .:::::::        ::
        ::.     .:::.        .:::.    .:::::.          .::
         ::.    .:::.        .:::.  .:::::            .::.
          :::.  .:::.        .:::.  ::::::          .:::. 
           .:::..::::.      .::::. .:::::::.      .:::.   
             .::::::::::::::::..:::::. :::::::::::::.     
                :::   ..::..     ...     .:::::::.        
                :::                                       
                .::        

----------------------------------------------------------------------
 Barak Pizzuto
______________________________________________________________________
 Micro-Epsilon

 barak.pizzuto@micro-epsilon.com
 8120 Brownleigh Dr.
 Raleigh, NC 27617
______________________________________________________________________
----------------------------------------------------------------------

Welcome to the Example code library! These examples are intended to 
provide an entry point into working with Micro-Epsilon sensors. The 
example library is NOT an exhaustive look at all sensor features and 
settings, but is rather a good starting point to help jumpstart the 
development process and show examples of typical calling structures. 
The example code should be used as a tool to speed up understanding of 
the base documentation which is still the most useful and relevant source
of information on the libraries! 

----------------------------------------------------------------------
______________________________________________________________________
 
 IMS5600 Example Description and Set-up
______________________________________________________________________
----------------------------------------------------------------------

To run the IMS5600 example some dependencies and setup are required

install python
-install Python from python.org
	https://www.python.org/downloads/

	***IMPORTANT*** to make life easier when running the installer
	select "add python to PATH". If running python commands in the 
	terminal for example, then it will make commands recognizable 
	without needing to specify the full path of Python. 

	If for some reason you can not do this, then to make your life 
	easier the default path of python can be found in a subfolder 
	of the AppData folder of Windows. This can be accessed by 
	typing in %appdata% to the file explorer directory and then 
	going up a folder to AppData. Then from AppData the file path to 
	Python is:
	AppData/Local/Programs/Python/Python3xx

install python packages
-python comes with many default packages which can be imported, but 
 often times additional packages are desired to add special functions to 
 Python. For this example two packages are needed to run. 

	Install keyboard 
	_____________________________________________________________
	-run the command below in the terminal to install 
	pip install keyboard


----------------------------------------------------------------------
______________________________________________________________________

Jupyter Notebook:
______________________________________________________________________
----------------------------------------------------------------------

Within this folder is an ipynb file which is a special jupyter source
file. This file contains a mix of markdown and code which can be run
in separated snippets. This allows for a better understanding of 
function calls as well as opportunity to adapt sample code down the 
line with new examples. This also includes things like snippets from 
documentation to conglomerate information in one place to make learning
the library as easy as possible. It is easiest to view this file within
an IDE that supports this like VS Code to have full control over the 
notebook. 

----------------------------------------------------------------------
----------------------------------------------------------------------
______________________________________________________________________

Running Commands: 
______________________________________________________________________
----------------------------------------------------------------------

If you are already familiar with Python and how to run code, you can 
simply follow your preferred procedure. 

The easiest method to run is to have an IDE like VSCode which can simply
run the code for you as needed. If you work without an IDE that can just
run the code like notepad, then you can run code in the terminal by:

changing directory to this directory where the code is
cd <file_path>

then if you added python to PATH you can simply call 
python IMS5600.py

----------------------------------------------------------------------