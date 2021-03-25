# Net-Snapshot
Network Operational State capture and analysis tool

&nbsp;

# Project Description
Powered by the pyATS libraries, this tool allows an administrator to take network operational state captures (snapshot) of a live network. And then analyze the results to determine what operational state changes have occurred. The entire applications runs within a single Docker container. 

A few possible use cases:
- NetDevOps customer demos
- Occasional network health checks
- Pre vs Post change analysis for scheduled maintenance or other network events
- Integration into an existing automated workflow (eg CI/CD) or change control process using the API

&nbsp;
&nbsp;

# Installation Steps:

&nbsp;

1. Install Docker or Docker Desktop, for Windows or MAC. Download site for Docker Desktop is below

   https://www.docker.com/products/docker-desktop
   
   Note: Step #1 can be skipped if Docker or Docker Desktop is already installed

&nbsp;

2. Install GIT. Download site for GIT is below

   https://git-scm.com/book/en/v2/Getting-Started-Installing-Git

&nbsp;
   
3. **Only for Windows 10 machines** (You can skip this step if using a non-Windows OS)

   Enter the below commands to ensure text files in cloned repository have LF line endings:

   git config --global core.eol lf
   
   git config --global core.autocrlf input

&nbsp;
   
4. Select install directory and clone the app's GitHub repo

   [directory-of-choice]

   git clone https://wwwin-github.cisco.com/davwill3/net-snapshot.git

&nbsp;
   
5. Initialize and run application container (**Ensure you are not connected to the VPN for this step**)

   cd net-snapshot/build
   
   docker-compose build

&nbsp;

   ***Note: The first time you run "docker-compose build" it will take a few minutes to download and install packages***
   ***Internet Access Is Required the first time you run "docker-compose build"***

&nbsp;

At this point the app is installed. You just need to start it. See Next step

&nbsp;


# How to Start

To start the Net-Snapshot app enter the single command below command

   docker-compose up
   
   &nbsp;

   Note: You must be in the net-snapshot/build for this to run successfully
   
 &nbsp;


The application should be up at this point, listening on TCP port 5000

Open web browser and try to connect   https://<your_IP>:5000/

The web server has a self-signed certificate, so expect a browser warning. Best to use Firefox or IE/Edge to easily ignore sellf signed certificate warning. 



# How to Stop

To stop the Net-Snapshot app enter the below command sequence

   Ctrl+c
   
      
   &nbsp;


&nbsp;


# How to Use:



<ins>Steps to load your topology </ins>


Two Options:

&nbsp;

1. Define Device Topology in a CSV file

   In Net-Snapshot Web UI, select "Upload Device List" Tab
   
   Download sample CSV file and enter a row per-device.
   

&nbsp;  

 Or

&nbsp;

 
2.  Manually define Device Topology in a YAML File 

   Place the Yaml topology file in the "net-snapshot/mount" directory. File must be named "topology.yaml"

   Sample topology file can be found at "net-snapshot/mount/topology.yaml"
   
&nbsp;  
&nbsp;

<ins>Steps to perform operational state capture (Snapshot)</ins>:

1. Select "Collect" tab

2. Choose one or more operational state capture options in addition to one or more devices. 

3. Select "Capture" button to begin capture
       
       Note: Job ID is presented once the capture process begins. Once the capture completes, the job ID should be visible on the home page. 

&nbsp;  
&nbsp;

<ins>Steps to compare two operational state captures</ins>:

1. Select "Compare" tab

2. Select two job IDs from the list of captures

3. Select "Compare" button 

       Note: The the operational state changes between the two captures will be presented. If no changes are presented, no differences were detected between the two operational state captures. 

&nbsp;  
&nbsp;


# Supported Operational State captures:


<ins>OSPF Interfaces</ins> - Capture state of OSPF enabled interfaces

<ins>OSPF SPF Runs</ins> - Capture the number of times OSPF SPF calculations have been performed. 

<ins>OSPF Neighbors</ins> -  Capture state of OSPF neighbor adjacencies  

<ins>BGP Neighbors</ins> - Capture state of BGP neighbor adjacency changes

<ins>EIGRP Neighbors</ins> -  Capture state of EIGRP neighbor adjacency changes     
  
<ins>Route Table Changes</ins> - Capture state of IPV4 route tabling

<ins>HSRP</ins> - Capture state of HSRP

<ins>Packet Fragmentation</ins> - Capture state of IP fragmentation (only IOS and IOS-XE devices supported)

<ins>Interfaces</ins> - Capture state of Interface counters. Interface up/down status, input errors, output drops, speed, duplex,  interface mtu, and switchport mode (only applies to L2 interfaces).

<ins>DMVPN</ins> - For DMVPN hubs. Captures state of registered DMVPN spoke routers.

&nbsp;  
&nbsp;


# Supported API Calls

<ins>List Jobs/Captures</ins>

* **URL**

  /api/list

* **Method:**
  
  GET
  
* **Data Params**

  N/A

* **Success Response:**
  
  
  * **Code:** 200 <br />
    **Content:** list of jobs/captures
    

* **Sample API Call:**

  curl -k -G https://localhost:5000/api/list
  
&nbsp;  

<ins>Delete Jobs/Captures</ins>

* **URL**

  /api/delete

* **Method:**
  
  POST
  
* ** Required Data Params**

  One or more Job_IDs in array format (ex. ["Job_32323"])
 
* **Success Response:**
  
  
  * **Code:** 200 <br />
    **Content:** list of jobs/captures
    

* **Sample Call:**

  curl -k --header "Content-Type: application/json" \
  --request POST \
  --data '{"Jobs": ["Job_32323"]}' \
  https://localhost:5000/api/delete

&nbsp;

<ins>Perform Device Snapshot</ins>

* **URL**

  /api/collect

* **Method:**
  
  POST
  
* **Data Params**

  One or more operational state captures (tasks) in array format
  One or more device in array format


* **Success Response:**
  
  
  * **Code:** 200 <br />
    **Content:** New Job ID returned   ex) {"job": "Job_18918", "status": "success"}
    

* **Sample Call:** (takes one or more Job_IDs in array format)
  
  curl -k --header "Content-Type: application/json" \
  --request POST \
  --data '{"Tasks": ["interface_state"], "Devices": ["Device_A", "Device_B", "Device_C"]}' \
  https://localhost:5000/api/collect

&nbsp;


<ins>Compare Snapshots</ins>

* **URL**

  /api/compare

* **Method:**
  
  POST
  
* **Data Params**

  Two Job IDs (Job_4597), in array format

* **Success Response:**
  
  
  * **Code:** 200 <br />
    **Content:**  List of operational state changes/differences between the two Job IDs
    

* **Sample Call:**
  
  curl -k --header "Content-Type: application/json" \
  --request POST \
  --data '{"Jobs": ["Job_4597", "Job_21146"]}' \
  https://localhost:5000/api/compare

&nbsp;
