# architecture_big_data
Scraping, Data Management, hdfs, Airflow, Medallion Architecture


### Docker
AzureAD+DeepKalyan@deep MINGW64 ~/IPSSI/23_Architecture_Big_Data/tp_architecture_big_data_ (INGESTION_BRONZE)
-- $ docker compose up -d

---------------------
check if user exist
(airflow)airflow users list

then delete
airflow users delete --username admin

then create
airflow users create \
  --username admin \
  --password admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com> > > > > >

  
Conversation avec Gemini
tp_architecture_big_data/ │ ├── dags/ ← Airflow DAGs │ ├── nbb_dag.py │ ├── notaire_dag.py │ ├── ingestion/ │ ├── nbb.py ← your consult.py cleaned │ ├── notaire.py ← your stapor.py cleaned │ ├── state.py ← State DB logic (NEW) │ ├── mongo.py ← Mongo connection (NEW) │ ├── data/ │ ├── bronze/ │ ├── docker/ │ ├── docker-compose.yml │ ├── notaire_cookies.json



I'm in tp_architecture_big_data



Give me script to create all these

Here is a quick bash script to generate that entire directory structure and create the empty files for you in one shot.

Run this command from your terminal while you are inside the tp_architecture_big_data directory:

Bash
mkdir -p dags ingestion data/bronze docker && \
touch dags/nbb_dag.py \
      dags/notaire_dag.py \
      ingestion/nbb.py \
      ingestion/notaire.py \
      ingestion/state.py \
      ingestion/mongo.py \
      docker/docker-compose.yml \
      docker/notaire_cookies.json
What this does:
mkdir -p: Creates the dags, ingestion, data/bronze, and docker folders simultaneously (and won't throw an error if they already exist).

touch: Creates all the specified empty files inside their respective folders.

If you want to verify it looks exactly like your plan, you can run tree (if installed) or ls -R right after!

apache airflow default password? or will I find?

It depends entirely on how you are running Apache Airflow. Here is exactly where you will find it or how to set it:

1. If you are using the official Docker Compose
If you downloaded the official docker-compose.yaml file from Apache Airflow, the default credentials are automatically created for you:

Username: airflow

Password: airflow

2. If you ran airflow standalone (Local/Pip install)
If you installed Airflow via pip on your local machine and ran airflow standalone, it automatically generates a random password for security.

Username: admin

Password: Look directly at your terminal logs where you ran the command. You will see a block of text that looks like this:

Plaintext
standalone | Airflow is ready
standalone | Login with username: admin password: SOME_RANDOM_PASSWORD
Alternative: It also saves this password in your ~/airflow/ directory. You can view it by running:

Bash
cat ~/airflow/standalone_admin_password.txt
3. If you want to force-create your own Admin User
If you can't find it, or if your container didn't generate one, you can manually create an admin user right now.

Via Docker Compose:

Bash
docker-compose run airflow-worker airflow users create --username admin --password admin --role Admin --firstname John --lastname Doe --email admin@example.com
Via Local Terminal:

Bash
airflow users create --username admin --password admin --role Admin --firstname John --lastname Doe --email admin@example.com
Which method are you using to run your Airflow instance?

I run with docker can't connect, it is telling invalid

If airflow / airflow is giving you an "Invalid username or password" error, it usually means your specific docker-compose.yml environment didn't automatically run the user initialization script, or it requires explicit environment variables.

You can fix this completely by manually injecting a brand-new administrator account directly into your running containers.

The Quick Fix: Create an Admin User Manually
Run this command inside your docker/ folder (or wherever your docker-compose.yml file lives):

Bash
docker compose run airflow-webserver airflow users create \
    --username admin \
    --password admin \
    --role Admin \
    --firstname Admin \
    --lastname User \
    --email admin@example.com
Once that command finishes successfully, go back to your browser and log in using:

Username: admin

Password: admin

Why Did This Happen?
If you wrote your own custom docker-compose.yml file from scratch (instead of using the massive, official 500-line quickstart file), it lacks the automatic setup step. Airflow starts up with a completely blank metadata database, so no user profiles exist until you explicitly create one!

AzureAD+DeepKalyan@deep MINGW64 ~/IPSSI/23_Architecture_Big_Data/tp_architecture_big_data_ (INGESTION_BRONZE)

$ docker compose run airflow-webserver airflow users create \

    --username admin \

    --password admin \

    --role Admin \

    --firstname Admin \

    --lastname User \

    --email admin@example.com

no configuration file provided: not found

Ah, you got the no configuration file provided: not found error because Docker Compose cannot find your docker-compose.yml file in your current folder.

Looking at your terminal path:
~/IPSSI/23_Architecture_Big_Data/tp_architecture_big_data_

According to the project structure we created earlier, your docker-compose.yml file lives inside the docker/ subfolder.

You have two ways to fix this:

Option 1: Move into the docker folder first (Recommended)
Navigate into the folder where the file actually lives, then run the command:

Bash
cd docker
docker compose run airflow-webserver airflow users create \
    --username admin \
    --password admin \
    --role Admin \
    --firstname Admin \
    --lastname User \
    --email admin@example.com
Option 2: Point directly to the file from where you are
If you prefer to stay in your current directory, you must use the -f flag to tell Docker exactly where the file is:

Bash
docker compose -f docker/docker-compose.yml run airflow-webserver airflow users create \
    --username admin \
    --password admin \
    --role Admin \
    --firstname Admin \
    --lastname User \
    --email admin@example.com


AzureAD+DeepKalyan@deep MINGW64 ~/IPSSI/23_Architecture_Big_Data/tp_architecture_big_data_/docker (INGESTION_BRONZE)

$ cd docker

docker compose run airflow-webserver airflow users create \

    --username admin \

    --password admin \

    --role Admin \

    --firstname Admin \

    --lastname User \

    --email admin@example.com

bash: cd: docker: No such file or directory

time="2026-06-30T14:40:51+02:00" level=warning msg="C:\\Users\\DeepKalyan\\IPSSI\\23_Architecture_Big_Data\\tp_architecture_big_data_\\docker\\docker-compose.yml: the attribute `version` is obsolete,it will be ignored, please remove it to avoid potential confusion"

no such service: airflow-webserver

It looks like two things happened here:

You were already inside the docker folder when you ran the command (notice your prompt ended in .../tp_architecture_big_data_/docker), which is why cd docker gave you a "No such file or directory" error. But Docker did find your docker-compose.yml file!

no such service: airflow-webserver: This means your docker-compose.yml file doesn't have a service named airflow-webserver. You are likely using a different name for your Airflow service (e.g., airflow, webserver, airflow-init, etc.).

Let's find out exactly what your service is named so we can fix this.

Step 1: Check your service names
Run this command to see the list of services defined in your file:

Bash
docker compose config --services
Step 2: Run the command with your actual service name
Look at the output from Step 1. Replace YOUR_SERVICE_NAME in the command below with whatever service represents your Airflow instance (often just webserver or airflow in custom setups):

Bash
docker compose run YOUR_SERVICE_NAME airflow users create \
    --username admin \
    --password admin \
    --role Admin \
    --firstname Admin \
    --lastname User \
    --email admin@example.com
(Note: You can safely ignore that warning about the version attribute being obsolete—Docker handles it automatically now!)

AzureAD+DeepKalyan@deep MINGW64 ~/IPSSI/23_Architecture_Big_Data/tp_architecture_big_data_/docker (INGESTION_BRONZE)

$ docker compose config --services

time="2026-06-30T14:41:59+02:00" level=warning msg="C:\\Users\\DeepKalyan\\IPSSI\\23_Architecture_Big_Data\\tp_architecture_big_data_\\docker\\docker-compose.yml: the attribute `version` is obsolete,it will be ignored, please remove it to avoid potential confusion"

mongo

airflow

Perfect, your service is simply named airflow!

Since it's a unified or single airflow service container, run this command to create your admin user:

Bash
docker compose run airflow airflow users create \
    --username admin \
    --password admin \
    --role Admin \
    --firstname Admin \
    --lastname User \
    --email admin@example.com
Once that finishes, you'll be able to log in at http://localhost:8080 (or whichever port you exposed) using:

Username: admin

Password: admin

AzureAD+DeepKalyan@deep MINGW64 ~/IPSSI/23_Architecture_Big_Data/tp_architecture_big_data_/docker (INGESTION_BRONZE)

$ docker compose run airflow airflow users create \

    --username admin \

    --password admin \

    --role Admin \

    --firstname Admin \

    --lastname User \

    --email admin@example.com

time="2026-06-30T14:43:05+02:00" level=warning msg="C:\\Users\\DeepKalyan\\IPSSI\\23_Architecture_Big_Data\\tp_architecture_big_data_\\docker\\docker-compose.yml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion"

[+] Creating 1/1

 ✔ Container mongo  Running                                                                    0.0s 





Please confirm database initialize (or wait 4 seconds to skip it). Are you sure? [y/N]

[2026-06-30T12:43:15.991+0000] {db.py:897} INFO - Log template table does not exist (added in 2.3.0); skipping log template sync.

/home/airflow/.local/lib/python3.8/site-packages/flask_limiter/extension.py:336 UserWarning: Using the in-memory storage for tracking rate limits as no storage was explicitly specified. This is not recommended for production use. See: https://flask-limiter.readthedocs.io#configuring-a-storage-backend for documentation about configuring the storage backend.

[2026-06-30T12:43:16.239+0000] {override.py:855} INFO - Security DB not found Creating all Models from Base

[2026-06-30T12:43:16.491+0000] {override.py:857} INFO - Security DB Created

[2026-06-30T12:43:16.500+0000] {override.py:1369} INFO - Inserted Role: Admin

[2026-06-30T12:43:16.506+0000] {override.py:1369} INFO - Inserted Role: Public

[2026-06-30T12:43:16.508+0000] {override.py:868} WARNING - No user yet created, use flask fab command to do it.

[2026-06-30T12:43:16.554+0000] {override.py:1769} INFO - Created Permission View: can edit on Passwords

[2026-06-30T12:43:16.560+0000] {override.py:1820} INFO - Added Permission can edit on Passwords to role Admin

[2026-06-30T12:43:16.569+0000] {override.py:1769} INFO - Created Permission View: can read on Passwords

[2026-06-30T12:43:16.575+0000] {override.py:1820} INFO - Added Permission can read on Passwords to role Admin

[2026-06-30T12:43:16.589+0000] {override.py:1769} INFO - Created Permission View: can edit on My Password

[2026-06-30T12:43:16.595+0000] {override.py:1820} INFO - Added Permission can edit on My Password to role Admin

[2026-06-30T12:43:16.602+0000] {override.py:1769} INFO - Created Permission View: can read on My Password

[2026-06-30T12:43:16.607+0000] {override.py:1820} INFO - Added Permission can read on My Password to role Admin

[2026-06-30T12:43:16.620+0000] {override.py:1769} INFO - Created Permission View: can edit on My Profile

[2026-06-30T12:43:16.627+0000] {override.py:1820} INFO - Added Permission can edit on My Profile to role Admin

[2026-06-30T12:43:16.633+0000] {override.py:1769} INFO - Created Permission View: can read on My Profile

[2026-06-30T12:43:16.639+0000] {override.py:1820} INFO - Added Permission can read on My Profile to role Admin

[2026-06-30T12:43:16.724+0000] {override.py:1769} INFO - Created Permission View: can create on Users

[2026-06-30T12:43:16.729+0000] {override.py:1820} INFO - Added Permission can create on Users to role Admin

[2026-06-30T12:43:16.736+0000] {override.py:1769} INFO - Created Permission View: can read on Users

[2026-06-30T12:43:16.742+0000] {override.py:1820} INFO - Added Permission can read on Users to role Admin

[2026-06-30T12:43:16.748+0000] {override.py:1769} INFO - Created Permission View: can edit on Users

[2026-06-30T12:43:16.754+0000] {override.py:1820} INFO - Added Permission can edit on Users to role Admin

[2026-06-30T12:43:16.764+0000] {override.py:1769} INFO - Created Permission View: can delete on Users

[2026-06-30T12:43:16.771+0000] {override.py:1820} INFO - Added Permission can delete on Users to role Admin

[2026-06-30T12:43:16.786+0000] {override.py:1769} INFO - Created Permission View: menu access on List Users

[2026-06-30T12:43:16.792+0000] {override.py:1820} INFO - Added Permission menu access on List Users to role Admin

[2026-06-30T12:43:16.804+0000] {override.py:1769} INFO - Created Permission View: menu access on Security

[2026-06-30T12:43:16.811+0000] {override.py:1820} INFO - Added Permission menu access on Security to role Admin

[2026-06-30T12:43:16.832+0000] {override.py:1769} INFO - Created Permission View: can create on Roles

[2026-06-30T12:43:16.839+0000] {override.py:1820} INFO - Added Permission can create on Roles to role Admin

[2026-06-30T12:43:16.847+0000] {override.py:1769} INFO - Created Permission View: can read on Roles

[2026-06-30T12:43:16.852+0000] {override.py:1820} INFO - Added Permission can read on Roles to role Admin

[2026-06-30T12:43:16.860+0000] {override.py:1769} INFO - Created Permission View: can edit on Roles

[2026-06-30T12:43:16.866+0000] {override.py:1820} INFO - Added Permission can edit on Roles to role Admin

[2026-06-30T12:43:16.872+0000] {override.py:1769} INFO - Created Permission View: can delete on Roles

[2026-06-30T12:43:16.879+0000] {override.py:1820} INFO - Added Permission can delete on Roles to role Admin

[2026-06-30T12:43:16.891+0000] {override.py:1769} INFO - Created Permission View: menu access on List Roles

[2026-06-30T12:43:16.897+0000] {override.py:1820} INFO - Added Permission menu access on List Roles to role Admin

[2026-06-30T12:43:16.918+0000] {override.py:1769} INFO - Created Permission View: can read on User Stats Chart

[2026-06-30T12:43:16.924+0000] {override.py:1820} INFO - Added Permission can read on User Stats Chart to role Admin

[2026-06-30T12:43:16.936+0000] {override.py:1769} INFO - Created Permission View: menu access on User's Statistics

[2026-06-30T12:43:16.943+0000] {override.py:1820} INFO - Added Permission menu access on User's Statistics to role Admin

[2026-06-30T12:43:16.965+0000] {override.py:1769} INFO - Created Permission View: can read on Permissions

[2026-06-30T12:43:16.971+0000] {override.py:1820} INFO - Added Permission can read on Permissions to role Admin

[2026-06-30T12:43:16.983+0000] {override.py:1769} INFO - Created Permission View: menu access on Actions

[2026-06-30T12:43:16.989+0000] {override.py:1820} INFO - Added Permission menu access on Actions to role Admin

[2026-06-30T12:43:17.011+0000] {override.py:1769} INFO - Created Permission View: can read on View Menus

[2026-06-30T12:43:17.017+0000] {override.py:1820} INFO - Added Permission can read on View Menus to role Admin

[2026-06-30T12:43:17.060+0000] {override.py:1769} INFO - Created Permission View: menu access on Resources

[2026-06-30T12:43:17.069+0000] {override.py:1820} INFO - Added Permission menu access on Resources to role Admin

[2026-06-30T12:43:17.106+0000] {override.py:1769} INFO - Created Permission View: can read on Permission Views

[2026-06-30T12:43:17.113+0000] {override.py:1820} INFO - Added Permission can read on Permission Views to role Admin

[2026-06-30T12:43:17.127+0000] {override.py:1769} INFO - Created Permission View: menu access on Permission Pairs

[2026-06-30T12:43:17.133+0000] {override.py:1820} INFO - Added Permission menu access on Permission Pairs to role Admin

[2026-06-30T12:43:17.732+0000] {override.py:1458} INFO - Added user admin

User "admin" created with role "Admin"

--------------

still

Username: admin

Password: admin

not working

The logs show that your user profile was created perfectly:
User "admin" created with role "Admin"

If admin / admin is still failing, it usually means your webserver container is either caching an old state or pointing to a different SQLite database file than the one the docker compose run command just initialized.

Let's do a hard reset on the containers to force them to read the newly updated database.

1. Hard Restart Your Services
Run these commands from inside your docker/ directory to force everything to sync:

Bash
# Stop and completely remove the current containers
docker compose down

# Start them up fresh in the background
docker compose up -d
2. Wait 10 seconds, then try logging in again
Go back to your browser, refresh the page (http://localhost:8080), and attempt to log in with:

Username: admin

Password: admin

Still blocked? Check this one setting:
If it still fails, look inside your docker-compose.yml file. If you have multiple services (like a separate airflow-webserver and airflow-scheduler or just a single airflow container acting as a webserver), make sure they share the exact same volume or database connection string (AIRFLOW__DATABASE__SQL_ALCHEMY_CONN).

If they use an in-memory or un-mapped local SQLite file (airflow.db), the run command creates the user inside a temporary container, and the main webserver container never sees it!

still fails

here is my docker-compose.yml:

------

version: '3.8'



services:



  mongo:

    image: mongo:6

    container_name: mongo

    ports:

      - "27017:27017"

    volumes:

      - mongo_data:/data/db



  airflow:

    image: apache/airflow:2.8.1

    container_name: airflow

    depends_on:

      - mongo

    environment:

      - AIRFLOW__CORE__LOAD_EXAMPLES=False

    volumes:

      - ../dags:/opt/airflow/dags

    ports:

      - "8080:8080"

    command: standalone



volumes:

  mongo_data:

Ah, seeing your docker-compose.yml makes the problem instantly clear!

Because your airflow service is running the standalone command, Airflow initializes itself completely from scratch inside the container's temporary filesystem every single time you use docker compose run.

When you ran docker compose run airflow airflow users create, Docker spun up a brand new, isolated temporary container, created the user inside it, and then destroyed it when it finished. Your main running container never saw it because they don't share a database volume!

Here is how to fix this permanently.

Option 1: Create the user inside the already running container (Easiest)
Since your container is already running, you need to execute the command directly inside that active environment using docker exec instead of docker compose run:

Bash
docker exec -it airflow airflow users create \
    --username admin \
    --password admin \
    --role Admin \
    --firstname Admin \
    --lastname User \
    --email admin@example.com
Try this right now, and admin / admin will work instantly at http://localhost:8080.

Option 2: The Right Way (Persist your Airflow Data)
Right now, if you restart your Docker containers, you will lose your admin user, your DAG history, and your connections. To fix this, you need to mount a volume for Airflow's database, just like you did for MongoDB.

Update your docker-compose.yml to look like this:

YAML
version: '3.8'

services:
  mongo:
    image: mongo:6
    container_name: mongo
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

  airflow:
    image: apache/airflow:2.8.1
    container_name: airflow
    depends_on:
      - mongo
    environment:
      - AIRFLOW__CORE__LOAD_EXAMPLES=False
    volumes:
      - ../dags:/opt/airflow/dags
      - airflow_data:/opt/airflow     # <--- ADD THIS to persist your database & logs
    ports:
      - "8080:8080"
    command: standalone

volumes:
  mongo_data:
  airflow_data:                       # <--- ADD THIS
If you update your file to this version, run docker compose down and docker compose up -d. After doing that, run the Option 1 (docker exec) command one last time, and your login credentials will be saved forever!

option 2 doesn't work

option 1



AzureAD+DeepKalyan@deep MINGW64 ~/IPSSI/23_Architecture_Big_Data/tp_architecture_big_data_/docker (INGESTION_BRONZE)

$ docker exec -it airflow airflow users create \

    --username admin \

    --password admin \

    --role Admin \

    --firstname Admin \

    --lastname User \

    --email admin@example.com

/home/airflow/.local/lib/python3.8/site-packages/flask_limiter/extension.py:336 UserWarning: Using the in-memory storage for tracking rate limits as no storage was explicitly specified. This is not recommended for production use. See: https://flask-limiter.readthedocs.io#configuring-a-storage-backend for documentation about configuring the storage backend.

admin already exist in the db 

If it says admin already exist in the db, then Option 1 successfully talked to your active container!

However, because you are running Airflow in standalone mode, it automatically initializes an admin user behind the scenes with a randomly generated password on its very first boot, which is why it's blocking you from creating a new one named admin.

Since the account already exists, we just need to forcefully reset its password to admin.

Run this command to override the existing password:

Bash
docker exec -it airflow airflow users reset-password \
    --username admin \
    --password admin
Once you see a success message, head over to http://localhost:8080 and log in with admin / admin. You are good to go!

AzureAD+DeepKalyan@deep MINGW64 ~/IPSSI/23_Architecture_Big_Data/tp_architecture_big_data_/docker (INGESTION_BRONZE)

$ docker exec -it airflow airflow users reset-password \

    --username admin \

    --password admin

Usage: airflow users [-h] COMMAND ...



Manage users



Positional Arguments:

  COMMAND

    add-role   Add role to a user

    create     Create a user

    delete     Delete a user

    export     Export all users

    import     Import users

    list       List users

    remove-role

               Remove role from a user



Optional Arguments:

  -h, --help   show this help message and exit



airflow users command error: argument COMMAND: invalid choice: 'reset-password' (choose from 'add-role', 'create', 'delete', 'export', 'import', 'list', 'remove-role'), see help above.



AzureAD+DeepKalyan@deep MINGW64 ~/IPSSI/23_Architecture_Big_Data/tp_architecture_big_data_/docker (INGESTION_BRONZE)

$  

Ah, my mistake! Airflow handles updating users through the regular create command or by deleting the old one first, rather than a reset-password subcommand.

Since the CLI is telling you admin already exists, let's just delete that existing auto-generated user and recreate it with your password.

Run these two commands back-to-back:

1. Delete the existing admin user
Bash
docker exec -it airflow airflow users delete --username admin
2. Create the clean admin user
Bash
docker exec -it airflow airflow users create \
    --username admin \
    --password admin \
    --role Admin \
    --firstname Admin \
    --lastname User \
    --email admin@example.com
Now try logging in at http://localhost:8080 with admin / admin. This will clear out the auto-generated password block!

Verify it worked

Install MongoDB extension in VS Code OR use:



from ingestion.mongo import companies



print(companies.find_one())



-----------

explain better how can I test

To test if your Airflow and MongoDB environments are working and communicating properly, you have two great options: the visual way (VS Code Extension) or the code way (Python Script).

Here is exactly how to do both, step-by-step.

Method 1: The Visual Way (VS Code Extension)
This is the easiest way to visually inspect your database and make sure MongoDB is alive and storing data.

Install the Extension: Open VS Code, go to the Extensions tab (Ctrl+Shift+X), search for MongoDB for VS Code, and install it.

Connect to Docker MongoDB: * Click on the new MongoDB leaf icon on your left sidebar.

Click Connect with Connection String.

Enter the standard local MongoDB URI:

Plaintext
mongodb://localhost:27017
Verify: You should see your MongoDB instance appear in the sidebar. If you expand it, you will see the default databases (admin, config, local) and eventually your custom databases once your scrapers run.

Method 2: The Code Way (Python Script)
Since your project structure separates the MongoDB connection logic into ingestion/mongo.py, let's use that to test.

Step 1: Write your connection logic (ingestion/mongo.py)
Open your ingestion/mongo.py file and add the code to connect to the Docker container. (Inside the Docker network, the host name is mongo, but from your local machine, it is localhost).

Python
from pymongo import MongoClient

# Connect to the MongoDB container running on localhost
client = MongoClient("mongodb://localhost:27017/")

# Select your database (it will be created automatically if it doesn't exist)
db = client["tp_big_data"]

# Select your collection
companies = db["companies"]
Step 2: Create a quick test script
Create a temporary file in your root directory called test_mongo.py (or run this via an interactive python terminal):

Python
from ingestion.mongo import companies

# 1. Insert a fake company to see if it works
print("Inserting test data...")
test_id = companies.insert_one({"name": "IPSSI Test Corp", "status": "active"}).inserted_id
print(f"Successfully inserted document with ID: {test_id}")

# 2. Try to read it back
print("\nFetching data from MongoDB:")
result = companies.find_one({"name": "IPSSI Test Corp"})
print(result)
Step 3: Run the test
Make sure you are in your main project folder (tp_architecture_big_data/) and run:

Bash
python test_mongo.py
If it prints out the dictionary with an _id and "name": "IPSSI Test Corp", your MongoDB pipeline is 100% functional and ready for your DAGs!

Did the admin login for Airflow end up working after the user recreation?

I have created new containers, and again(with admin admin) I have issue of



Invalid login. Please try again.

Since you recreated the containers using Option 2 (with the airflow_data volume), Airflow started completely fresh. Because it is running in standalone mode, it instantly auto-generated a brand-new random password on its first boot and overrode your previous settings.

Let's fix this once and for all. Since your data is now persistent, you only have to do this one last time.

Run these two commands back-to-back right now:

1. Delete the auto-generated admin user
Bash
docker exec -it airflow airflow users delete --username admin
2. Re-create the admin user with your password
Bash
docker exec -it airflow airflow users create \
    --username admin \
    --password admin \
    --role Admin \
    --firstname Admin \
    --lastname User \
    --email admin@example.com
Now, go to http://localhost:8080, type in admin / admin, and you will be let right in. Because your volume is configured, this password will finally stick even if you restart the containers later!

PS C:\Users\DeepKalyan\IPSSI\23_Architecture_Big_Data\tp_architecture_big_data_\docker> docker exec -it airflow airflow users delete --username admin

/home/airflow/.local/lib/python3.8/site-packages/flask_limiter/extension.py:336 UserWarning: Using the in-memory storage for tracking rate limits as no storage was explicitly specified. This is not recommended for production use. See: https://flask-limiter.readthedocs.io#configuring-a-storage-backend for documentation about configuring the storage backend.

/home/airflow/.local/lib/python3.8/site-packages/flask_limiter/extension.py:336 UserWarning: Using the in-memory storage for tracking rate limits as no storage was explicitly specified. This is not recommended for production use. See: https://flask-limiter.readthedocs.io#configuring-a-storage-backend for documentation about configuring the storage backend.

User "admin" deleted

PS C:\Users\DeepKalyan\IPSSI\23_Architecture_Big_Data\tp_architecture_big_data_\docker> docker exec -it airflow airflow users create \    --username admin \    --password admin \    --role Admin \    --firstname Admin \    --lastname User \    --email admin@example.com

Usage: airflow [-h] GROUP_OR_COMMAND ...



Positional Arguments:

  GROUP_OR_COMMAND



    Groups

      config         View configuration

      connections    Manage connections

      dags           Manage DAGs

      db             Database operations

      jobs           Manage jobs

      pools          Manage pools

      providers      Display providers

      roles          Manage roles

      tasks          Manage tasks

      users          Manage users

      variables      Manage variables



    Commands:

      cheat-sheet    Display cheat sheet

      dag-processor  Start a standalone Dag Processor instance

      info           Show information about current Airflow and environment

      kerberos       Start a kerberos ticket renewer

      plugins        Dump information about loaded plugins

      rotate-fernet-key

                     Rotate encrypted connection credentials and variables

      scheduler      Start a scheduler instance

      standalone     Run an all-in-one copy of Airflow

      sync-perm      Update permissions for existing roles and optionally DAGs

      triggerer      Start a triggerer instance

      version        Show the version

      webserver      Start a Airflow webserver instance



Optional Arguments:

  -h, --help         show this help message and exit



airflow command error: unrecognized arguments: \ \ \ \ \ \, see help above.

PS C:\Users\DeepKalyan\IPSSI\23_Architecture_Big_Data\tp_architecture_big_data_\docker> 

You are so close! The user was successfully deleted (User "admin" deleted).

The error happened because you are using PowerShell (PS C:\...). PowerShell treats backslashes (\) as literal characters instead of line-breaks, which caused it to send \ \ \ \ \ straight to Airflow and break the command.

To fix it, copy and paste this single-line version of the command into your PowerShell terminal:

PowerShell
docker exec -it airflow airflow users create --username admin --password admin --role Admin --firstname Admin --lastname User --email admin@example.com
Once that runs, it will create your clean admin user with the admin password, and you can instantly log into the UI at http://localhost:8080!

Import "airflow.operators.python" could not be resolvedPylancereportMissingImports

(module) operators

Operators.

sphinx-autoapi-skip :

That reportMissingImports warning from Pylance happens because VS Code is running in your local machine's Python environment, but Apache Airflow is installed inside your Docker container. VS Code simply can't find the Airflow files on your local disk to provide autocomplete or type checking.

Here are the two ways to clean this up:

Method 1: Install Airflow locally for VS Code (Recommended)
The easiest way to make Pylance happy without breaking anything is to install a lightweight, constraint-free version of Airflow in your local virtual environment so VS Code can read its structure.

Activate your local virtual environment in your terminal (if you use one).

Run this pip command to install the Airflow package locally:

Bash
pip install apache-airflow
Restart your VS Code window (Ctrl+Shift+P -> Developer: Reload Window). The red squiggly lines will disappear!

Method 2: Tell Pylance to ignore it
If you don't want to install Airflow locally and just want the error to go away, you can tell Pylance to ignore the missing import directly in your Python code.

Add # type: ignore to the end of your import line like this:

Python
from airflow.operators.python import PythonOperator  # type: ignore
Alternatively, you can add a settings.json file inside a .vscode/ folder at the root of your project to turn off the warning globally for this workspace:

JSON
{
    "python.analysis.diagnosticSeverityOverrides": {
        "reportMissingImports": "none"
    }
}
pip install apache-airflow doesnot work

Ah, that makes sense. A plain pip install apache-airflow fails on Windows because Airflow is built exclusively for POSIX systems (Linux/macOS) and requires complex C-extensions that do not compile naturally on native Windows PowerShell.

Since your actual application is running flawlessly inside Docker anyway, we don't need to fight with installing full Airflow on Windows. We just need to trick VS Code's Pylance engine into recognizing the syntax.

Here are the two best workarounds to fix those red squiggly lines in VS Code:

Option 1: Install dummy-airflow (The Smart Trick)
There is a community package designed specifically for this scenario. It provides fake "stubs" (empty files with the exact same layout as Airflow) so your local IDE stops complaining, but it doesn't actually try to install the heavy Linux-only engine.

Run this in your PowerShell terminal:

PowerShell
pip install airflow-stubs
(If that doesn't resolve it, try pip install apache-airflow-stubs instead).

Option 2: Force VS Code to ignore the missing imports
If you don't want to install any more pip packages locally, you can configure your VS Code workspace to stop treating missing imports as an error.

Create a folder named .vscode at the root of your project directory (tp_architecture_big_data/).

Inside that folder, create a file named settings.json.

Paste the following configuration inside it:

JSON
{
    "python.analysis.diagnosticSeverityOverrides": {
        "reportMissingImports": "none"
    }
}
Once saved, restart VS Code (Ctrl+Shift+P -> type Developer: Reload Window). The errors will vanish, and you can write your Python DAG files in peace!

how to Activate your local virtual environment in your terminal 

To activate a virtual environment, you need to run the activation script that belongs to your environment's folder.

Because you are using PowerShell on Windows, the exact command depends on whether you have already created a virtual environment folder (usually named .venv or venv) in your project directory.

Here is how to do it based on your setup:

Step 1: Set your Execution Policy (PowerShell Only)
By default, Windows blocks PowerShell scripts from running. If you haven't done this already, you must run this command once to allow your virtual environment to turn on:

PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
Step 2: Activate your Environment
Choose the option below that fits your current situation:

Scenario A: You already have a .venv or venv folder
If you already created your environment inside tp_architecture_big_data_, run this command:

PowerShell
# If your folder is named .venv
.\.venv\Scripts\Activate.ps1

# If your folder is named venv
.\venv\Scripts\Activate.ps1
Scenario B: You haven't created a virtual environment yet
If you don't see a .venv folder in your project directory, you need to create one first, then activate it:

PowerShell
# 1. Create the environment
python -m venv .venv

# 2. Activate it
.\.venv\Scripts\Activate.ps1
How to know it worked?
Once activated, you will see the name of your environment in parentheses at the very beginning of your PowerShell prompt line, looking something like this:

(.venv) PS C:\Users\DeepKalyan\...>

To turn it off later when you are done, simply type deactivate.

(.venv) PS C:\Users\DeepKalyan\IPSSI\23_Architecture_Big_Data\tp_architecture_big_data_> docker compose restart

no configuration file provided: not found

Ah, you are seeing no configuration file provided: not found because you ran the command from your project root folder (tp_architecture_big_data_), but your docker-compose.yml file is inside the docker/ subfolder.

Whenever you run a docker compose command, Docker expects the configuration file to be in your current working directory unless you tell it otherwise.

You have two ways to fix this:

Option 1: Move into the docker folder first (Easiest)
Navigate into the folder where the file lives, then restart:

PowerShell
cd docker
docker compose restart
Option 2: Point directly to the file from where you are
If you want to stay in your root directory so you can keep editing your code files, use the -f flag to point to the file path:

PowerShell
docker compose -f docker/docker-compose.yml restart
docker compose restart

will I loose the volume?

No, you will not lose your data!

Running docker compose restart simply stops your running containers and starts them right back up again. It is completely safe.

Here is a quick breakdown of how Docker handles your volume data depending on the command you use:

Safe Commands (No Data Loss)
docker compose restart: Just reboots the containers. Your data remains perfectly intact.

docker compose stop: Freezes the containers without destroying them. Safe.

docker compose down: Stops and removes the containers entirely, but it leaves your volumes alone. Since your database data lives inside the mongo_data and airflow_data volumes on your hard drive, the data will instantly reappear the next time you run docker compose up -d.

The ONLY Command That Deletes Data
The only time you will ever lose your volume data is if you explicitly tell Docker to destroy it by adding the -v (volumes) flag:

PowerShell
# DANGER: This will wipe your MongoDB and Airflow databases completely clean
docker compose down -v
As long as you don't use that -v flag, your admin accounts, scrapers, and pipeline data are completely safe!

version: '3.8'



services:



  mongo:

    image: mongo:6

    container_name: mongo

    ports:

      - "27017:27017"

    volumes:

      - mongo_data:/data/db



  airflow:

    build:

      context: .

      dockerfile: Dockerfile

    container_name: airflow

    restart: always

    depends_on:

      - mongo

    environment:

      AIRFLOW__CORE__EXECUTOR: SequentialExecutor

      AIRFLOW__CORE__LOAD_EXAMPLES: "False"

      AIRFLOW__WEBSERVER__WORKERS: 1

      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: sqlite:////opt/airflow/airflow.db

    volumes:

      - ../dags:/opt/airflow/dags

      - ..:/opt/airflow/project

    ports:

      - "8080:8080"

    command: >

      bash -c "

      airflow db init &&

      airflow webserver &

      airflow scheduler

      "



  hadoop-namenode:

    image: bde2020/hadoop-namenode:2.0.0-hadoop3.2.1-java8

    container_name: namenode

    environment:

      - CLUSTER_NAME=test

    ports:

      - "9870:9870"

      - "9000:9000"

    volumes:

      - namenode-data:/hadoop/dfs/name



  hadoop-datanode:

    image: bde2020/hadoop-datanode:2.0.0-hadoop3.2.1-java8

    container_name: datanode

    environment:

      - CLUSTER_NAME=test

      - CORE_CONF_fs_defaultFS=hdfs://namenode:9000

    volumes:

      - datanode-data:/hadoop/dfs/data

    depends_on:

      - hadoop-namenode



  volumes:

    namenode-data:

    datanode-data:





volumes:

  mongo_data:

  # airflow_data:                       # <--- ADD THIS



Is it looks good to you? 

Looking closely at your new configuration, there are a few syntax errors and architectural issues that will prevent it from running correctly.

Here is a review of what needs fixing, followed by a corrected, ready-to-copy version.

What needs fixing:
The Indentation Bug (CRITICAL):
Your volumes: block at the very bottom defines namenode-data: and datanode-data: inside the indentation of the services block. Docker Compose will crash immediately with a parsing error. All named volumes must be defined at the absolute root level.

Missing Airflow Persistence:
You commented out # airflow_data:. Because your AIRFLOW__DATABASE__SQL_ALCHEMY_CONN points to /opt/airflow/airflow.db, your metadata database lives inside the container. If you recreate or update this container, you will lose your admin users and DAG run histories again. You need to map a named volume or directory to persist that .db file.

The Airflow command Backgrounding Process Loop:
Using airflow webserver & kicks the webserver to the background, and then runs airflow scheduler in the foreground. If the webserver crashes, Docker will never notice because it only monitors the foreground process (scheduler). For a small homework/TP environment like this, running Airflow's built-in standalone command is much safer and automatically manages both processes cleanly for you.

The Corrected docker-compose.yml
Here is the clean, fixed version of your file:

YAML
version: '3.8'

services:

  mongo:
    image: mongo:6
    container_name: mongo
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

  airflow:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: airflow
    restart: always
    depends_on:
      - mongo
    environment:
      AIRFLOW__CORE__LOAD_EXAMPLES: "False"
      AIRFLOW__WEBSERVER__WORKERS: 1
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: sqlite:////opt/airflow/persist/airflow.db
    volumes:
      - ../dags:/opt/airflow/dags
      - ..:/opt/airflow/project
      - airflow_data:/opt/airflow/persist  # Safely persists your sqlite file
    ports:
      - "8080:8080"
    command: standalone

  hadoop-namenode:
    image: bde2020/hadoop-namenode:2.0.0-hadoop3.2.1-java8
    container_name: namenode
    environment:
      - CLUSTER_NAME=test
    ports:
      - "9870:9870"
      - "9000:9000"
    volumes:
      - namenode-data:/hadoop/dfs/name

  hadoop-datanode:
    image: bde2020/hadoop-datanode:2.0.0-hadoop3.2.1-java8
    container_name: datanode
    environment:
      - CLUSTER_NAME=test
      - CORE_CONF_fs_defaultFS=hdfs://namenode:9000
    volumes:
      - datanode-data:/hadoop/dfs/data
    depends_on:
      - hadoop-namenode

# Root level volumes definitions fixed here
volumes:
  mongo_data:
  airflow_data:
  namenode-data:
  datanode-data:
Why the change to /opt/airflow/persist/airflow.db?
I adjusted your SQLite path slightly so it saves the database file inside a dedicated /persist folder. This ensures it maps directly to our airflow_data volume without colliding with your mapped code folders (/dags and /project). Your logins and pipeline histories are now fully safe!

PHASE 3 — Python access to HDFS

You need a Python client.

✅ Install in Airflow container

In Dockerfile: RUN pip install hdfs

Rebuild:

docker compose up --build -d



Didn't really understand where (Install in Airflow container) ?

just need to add in Dockerfile?

Yes, exactly! You just need to add it to your Dockerfile.

When the instructions say "Install in Airflow container", they mean that the hdfs Python package must be available inside the environment where your Airflow code runs (which is inside the Docker container, not just on your local Windows machine).

By putting it in the Dockerfile, Docker will bake the package right into the container image when it builds.

Here is exactly how to do it:

Step 1: Update your Dockerfile
Go to your project root (or wherever your Dockerfile is located) and make sure it looks like this:

Dockerfile
FROM apache/airflow:2.8.1

# Install the HDFS python client library
RUN pip install --no-cache-dir hdfs
Step 2: Rebuild and restart your containers
Run this command from your docker/ directory to force Docker to read your new Dockerfile modifications and rebuild the Airflow image:

PowerShell
docker compose up --build -d
Why do we do this?
Airflow will execute your DAGs inside the container. When your Python script tries to execute import hdfs, it looks at the container's internal Python libraries. Running RUN pip install hdfs during the build phase ensures that library is waiting and ready for Airflow to use!

PHASE 5 — Modify NBB ingestion (IMPORTANT)

Right now:





PDF → local file



Python



PDF → local file

Afficher plus de lignes

✅ Add HDFS upload

Inside nbb.py, after saving PDF:

✅ MODIFY:





pdf_path = download_pdf(session, deposit)



Python



pdf_path = download_pdf(session, deposit)





Afficher plus de lignes

✅ ADD:



from ingestion.hdfs_client import upload_to_hdfs



hdfs_path = f"/bronze/nbb/{bce}/{year}/{pdf_path.name}"

upload_to_hdfs(str(pdf_path), hdfs_path)





--------------------

didn't understand where, here is my nbb.py :



import time

import requests

import pandas as pd

from io import StringIO

from pathlib import Path

from typing import List, Dict

from ingestion.state import already_done, mark_done

from ingestion.hdfs_client import upload_to_hdfs



TMP = Path("data/bronze/nbb")

# TMP = Path("tmp/pdfs")

TMP.mkdir(parents=True, exist_ok=True)



BASE = "https://consult.cbso.nbb.be/api"



HEADERS = {

    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",

    "Accept": "application/json, text/plain, */*",

    "Accept-Language": "en-US,en;q=0.9",

    "sec-fetch-dest": "empty",

    "sec-fetch-mode": "cors",

    "sec-fetch-site": "same-origin",

}





def make_session(enterprise_number: str) -> requests.Session:

    session = requests.Session()

    session.headers.update(HEADERS)

    page_url = f"https://consult.cbso.nbb.be/consult-enterprise/{enterprise_number}"

    session.headers.update({"Referer": page_url})

    session.get(page_url)  # establishes ASLBSA, ASLBSACORS, JSESSIONID cookies

    return session





def get_deposits(session: requests.Session, enterprise_number: str) -> list:

    url = (

        f"{BASE}/rs-consult/published-deposits"

        f"?page=0&size=10&enterpriseNumber={enterprise_number}"

        f"&sort=periodEndDate,desc&sort=depositDate,desc"

    )

    r = session.get(url)

    r.raise_for_status()

    data = r.json()

    print(f"Found {data['totalElements']} filings ({data['totalPages']} pages). Loading first {len(data['content'])}.")

    return data["content"]





def download_csv(session: requests.Session, deposit_id: str) -> str:

    url = f"{BASE}/external/broker/public/deposits/consult/csv/{deposit_id}"

    r = session.get(url)

    r.raise_for_status()

    return r.text





def download_pdf(session: requests.Session, deposit: dict) -> Path:

    """Download PDF for a deposit and save to tmp/pdfs/. Returns the saved path."""

    deposit_id  = deposit["id"]

    year        = deposit["periodEndDateYear"]

    enterprise  = deposit["enterpriseNumber"]

    reference   = deposit["reference"]

    filename    = f"{enterprise}_{year}_{reference}.pdf"

    dest_dir        = TMP / enterprise / str(year)

    dest_dir.mkdir(parents=True, exist_ok=True)

    dest = dest_dir / filename





    if dest.exists():

        print(f"    PDF already exists: {filename}")

        return dest



    url = f"{BASE}/external/broker/public/deposits/pdf/{deposit_id}"

    r = session.get(url)

    r.raise_for_status()

    dest.write_bytes(r.content)

    print(f"    PDF saved: {filename} ({len(r.content) // 1024} KB)")

    return dest





def parse_csv(csv_text: str) -> dict:

    df = pd.read_csv(StringIO(csv_text), header=None, skiprows=1)

    codes = {}

    for _, row in df.iterrows():

        key = str(row[0]).strip()

        try:

            codes[key] = float(row[1])

        except (ValueError, TypeError):

            codes[key] = row[1]

    return codes





def compute_kpis(codes: dict) -> dict:

    def get(code):

        return codes.get(code, 0.0)



    omzet        = get("70")

    cogs         = get("60")

    depreciation = get("630")

    ebit         = get("9901")

    net_profit   = get("9904")

    cash         = get("54/58")

    equity       = get("10/15")

    total_assets = get("20/58")

    fin_debt     = get("17") + get("43")

    gross_profit = omzet - cogs

    ebitda       = ebit + depreciation



    def pct(num, denom):

        return round(num / denom * 100, 2) if denom else None



    return {

        "entity":           codes.get("Entity name"),

        "period_end":       codes.get("Accounting period end date"),

        "chiffre_affaires": omzet,

        "marge_brute":      gross_profit,

        "ebitda":           ebitda,

        "ebit":             ebit,

        "resultat_net":     net_profit,

        "taux_marge_brute": pct(gross_profit, omzet),

        "taux_ebitda":      pct(ebitda, omzet),

        "marge_nette":      pct(net_profit, omzet),

        "tresorerie":       cash,

        "dettes_fin":       fin_debt,

        "dette_nette":      fin_debt - cash,

        "fonds_propres":    equity,

        "total_actif":      total_assets,

        "autonomie_fin":    pct(equity, total_assets),

    }





def get_all_kpis(enterprise_number: str) -> List[Dict]:

    session = make_session(enterprise_number)

    deposits = get_deposits(session, enterprise_number)



    results = []

    for deposit in deposits:

        deposit_id = deposit["id"]

        year = deposit["periodEndDateYear"]

        bce = deposit["enterpriseNumber"]



        if already_done(bce, "nbb", deposit_id):

            print(f"  Skipping {year} (id={deposit_id})...")

            continue



        print(f"  Processing {year} (id={deposit_id})...")



        # Always attempt PDF download (works for all years including migrated)

        try:

            pdf_path = download_pdf(session, deposit)

            print("DEBUG: calling mark_done")

            mark_done(bce, "nbb", deposit_id, year, str(pdf_path))

        except Exception as e:

            print(f"    ✗ PDF failed for {year}: {e}")

        time.sleep(0.3)



        # CSV only available for non-migrated filings

        if deposit.get("migration"):

            print(f"    Skipping CSV for {year} (legacy/migrated filing)")

            continue



        try:

            csv_text = download_csv(session, deposit_id)

            codes = parse_csv(csv_text)

            kpis = compute_kpis(codes)

            kpis["year"] = year

            kpis["reference"] = deposit["reference"]

            results.append(kpis)

        except Exception as e:

            print(f"    ✗ CSV failed for {year}: {e}")

        time.sleep(0.3)



    return results





# # --- Run ---

# enterprise_number = "0203430576"  # Apple Retail Belgium

# kpis = get_all_kpis(enterprise_number)



# df = pd.DataFrame(kpis).set_index("year").sort_index(ascending=False)

# pd.set_option("display.float_format", "{:,.2f}".format)

# pd.set_option("display.max_columns", None)

# pd.set_option("display.width", 200)



# print("\n=== KPI Summary ===")

# print(df[["entity", "period_end", "chiffre_affaires", "ebitda", "resultat_net", "marge_nette", "autonomie_fin"]])

You need to insert that logic right inside your main orchestration loop in get_all_kpis.

The best spot is right after pdf_path = download_pdf(session, deposit) succeeds, but before you call mark_done. This guarantees that if the HDFS upload fails, the task will throw an error instead of mistakenly marking the file as finished.

Here is exactly how your modified get_all_kpis function loop should look. Notice the new try/except block where the PDF download occurs:

Python
def get_all_kpis(enterprise_number: str) -> List[Dict]:
    session = make_session(enterprise_number)
    deposits = get_deposits(session, enterprise_number)

    results = []
    for deposit in deposits:
        deposit_id = deposit["id"]
        year = deposit["periodEndDateYear"]
        bce = deposit["enterpriseNumber"]

        if already_done(bce, "nbb", deposit_id):
            print(f"  Skipping {year} (id={deposit_id})...")
            continue

        print(f"  Processing {year} (id={deposit_id})...")

        # Always attempt PDF download (works for all years including migrated)
        try:
            # 1. Download the file locally
            pdf_path = download_pdf(session, deposit)
            
            # === 2. ADD HDFS UPLOAD HERE ===
            hdfs_path = f"/bronze/nbb/{bce}/{year}/{pdf_path.name}"
            print(f"    Uploading PDF to HDFS: {hdfs_path}")
            upload_to_hdfs(str(pdf_path), hdfs_path)
            # ===============================

            print("DEBUG: calling mark_done")
            mark_done(bce, "nbb", deposit_id, year, str(pdf_path))
        except Exception as e:
            print(f"    ✗ PDF download or HDFS upload failed for {year}: {e}")
        time.sleep(0.3)

        # CSV only available for non-migrated filings
        if deposit.get("migration"):
            print(f"    Skipping CSV for {year} (legacy/migrated filing)")
            continue

        try:
            csv_text = download_csv(session, deposit_id)
            codes = parse_csv(csv_text)
            kpis = compute_kpis(codes)
            kpis["year"] = year
            kpis["reference"] = deposit["reference"]
            results.append(kpis)
        except Exception as e:
            print(f"    ✗ CSV failed for {year}: {e}")
        time.sleep(0.3)

    return results
Why this works perfectly here:
Inside this part of the loop, the variables bce and year have already been defined dynamically from the current deposit dictionary entry. Since you already imported upload_to_hdfs at the top of your file, it will now seamlessly catch each local PDF execution path and mirror it onto your Hadoop cluster.

I did docker compose up --build -d

now admin admin OR airflow airflow is not working what to do?

Because you completely rebuilt the containers using a new Dockerfile and a modified docker-compose.yml, Docker created a fresh container. Since you are using Airflow's standalone command, it automatically ran an internal initialization sequence on startup, generating a brand-new random password and ignoring the old one.

Let's fix it right now so you can log in. Since we added the airflow_data volume to your compose file, you will only have to do this one last time.

Open your PowerShell terminal and run these two commands back-to-back:

1. Delete the auto-generated admin user
PowerShell
docker exec -it airflow airflow users delete --username admin
2. Re-create the clean admin user
Copy and paste this single-line command into PowerShell to avoid line-break errors:

PowerShell
docker exec -it airflow airflow users create --username admin --password admin --role Admin --firstname Admin --lastname User --email admin@example.com



### Airflow
http://localhost:8080
Username: admin
Password: admin

### Mongo db 
to fill the mongo db with csv local files
python -m ingestion.load_companies

test in VS code the string to use after clicking on connect 
mongodb://localhost:27017

<!-- Create index -->
col.create_index("bce")

 docker exec -it mongo mongosh 

### Virtual environment
1. Create the environment
python -m venv .venv
2. Activate it
.\.venv\Scripts\Activate.ps1



pip install requests pandas pymongo playwright apache-airflow
playwright install