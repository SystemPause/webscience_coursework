# Web Science Coursework 

## Overview

This repository is specific for the WebScience Coursework taught at the University of Glasgow (2019/2020)

* Author: Alessandro Speggiorin
* StudentID: 2268690S

## Files 
The repository is organised as follows: 

* **NON-runnable files:**
	* **access_keys.py**: This file contains all the main configuration settings
	* **helper_functions.py**: A file containing most of the helper functions used 
	* **2268690s_notebook.ipynb**: Alternative solution presented as a Jupyter notebook
	* **requirements.txt**: All project dependencies 
	* **sampleData.json**: Sample Data
* **Runnable files**: Can be run with the command `python filename.py`
	* **q1\_streamListener.py**: Files for Q1 used to get Twitter data using the Streaming API 
	* **q1\_rest\_api.py**: Files for Q1 used to get Twitter data using the REST API 
	* **q2\_q3\_q4.py**: Run script in order to get results for questions 2-3-4

	
## Getting Started
### Installation 
* For the setup is assumed that Python3.6, Pip, MongoDB and all relevant packages are installed. 
* In order to install the specific dependencies needed for to run these files issue the following command 

```
pip install -r requirements.txt

```

### Modify the access_keys.py 

 * Open  the **access_keys.py** file and modify all the access_keys variables in order to be able to use and connect to twitter APIs successfully. 

```python
CONSUMER_KEY = 'CONSUMER_KEY'
CONSUMER_SECRET = 'CONSUMER_SECRET'
ACCESS_TOKEN = 'ACCESS_TOKEN'
ACCESS_TOKEN_SECRET = 'ACCESS_TOKEN_SECRET'
```

* The flag `UPLOAD_DATA_FROM_FILE` is used in order to upload data from a file.json (**has to be named sampleData.json**). The variable is set to `False` by default so data from **MongoDB** will be uploaded. 
	* If set to `True` then data from a file named **sampleData.json** will be loaded. 
	* Extra data can be then added by running **q1\_streamListener.py** or **q1\_rest\_api.py**. 

### Run Files
All these files can be run with the command `python filename.py`

* **q1\_streamListener.py** will run the Stream API to get UK based twitters. Runs indefinitely. Has to bo be interrupted. 
* **q1\_rest\_api.py** Gets 1000 UK based twitters following top topics. If the API key limit has been reached then the program waits for 15mins
* **q2\_q3\_q4.py** Runs all the operations required by task 2-3-4. Generated graphs and results are saved in the same directory. All other outputs are displayed in the terminal. **Would recommend running `python q2_q3_q4.py > output.txt` in order to inspect the output file.** 
	* To plot graphs for each network (users networks for mentions,re tweets, replies) set the flag `plot=True` in the function `generate_network(...)` provided in this file (for each of the networks). Be aware that plotting graphs takes few minutes. 


 	
