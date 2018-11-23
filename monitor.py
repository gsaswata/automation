import paramiko
import sys
import time
import sys
import Log

logger = Log.getLogger()
p = paramiko.SSHClient()
p.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Method to create a SSH connection to the remote server
def connect_server(hostname, user, password): 
    try:
        p.connect(hostname, 22, user, password)
        print("Connected to {}".format(hostname))
    except Exception as err:
        print("Unable to connect to {0} : {1}".format(hostname,err))
        sys.exit()


# Method to retrieve process information from remote server 
def process_list():
    try:
        stdin, stdout, stderr = p.exec_command('ps -ef | wc -l')
        proc = stdout.readlines()
        stdin, stdout, stderr = p.exec_command('ps -eo pid,%mem,cmd --sort=-%mem | head -n 6')
        mem = stdout.readlines()
    except Exception as err:
        logger.error("Error in getting process information : {}".format(err))
        return
    logger.info("--------TOP 5 MEMORY CONSUMING PROCESSES--------")
    for item in range(len(mem)):
        writeToFile(mem[item])
    return int(proc[0])

# Method to retrieve disk usage stats of /var
def diskUsage():
    try:
        stdin, stdout, stderr = p.exec_command("df -kh --output='pcent' /var | awk 'FNR==2 {print}'")
        pct = stdout.readlines()
    except Exception as err:
        logger.error("Error in getting disk usage information : {}".format(err))
        return
    return int(pct[0].strip('%\n'))

# Method to look for ERROR in syslog
def logparse(logFile):
    pos=logFile.tell()
    logFile.seek(pos)
    data=logFile.read()
    pos=logFile.tell()
    if 'ERROR' in (str(data.strip())):
        logger.error(str(data.strip()))
    else:
        logger.info("No error found in syslog")

# Write to log file
def writeToFile(text):
    try:
        monitorLog = open('systemlogs.log', 'a')
        monitorLog.write(text+'\n')
        monitorLog.close()
    except Exception as err:
        logger.error("Unable to write to log file : {}".format(err))


# Main
if __name__ == '__main__':
    # Check if no. of arguments are correct
    if len(sys.argv) < 5:
        print("\nOops!! Please check the arguments and run again")
        print("Usage : python monitor.py <host> <user> <password> <interval>\n")
        sys.exit()
    else:
        pass

    # Variables
    procList = []
    pcentList = []
    fileName = '/var/log/syslog'
    # Connect to the remote server and create a sftp session to read the log file   
    connect_server(sys.argv[1], sys.argv[2], sys.argv[3])
    sftp_client = p.open_sftp()
    logFile=sftp_client.file(fileName, 'r', -1)

    while True:
        # Write the retrieved process information or any errors to the log.
        proc_count = process_list()
        if proc_count is None:
            logger.error("Failed to retrieve information from host {}".format(sys.argv[1]))
        else:
            procList.append(proc_count)
            if len(procList) >= 2:
                procList = procList[-2:]
                diff = int(procList[1] - procList[0])
                if diff <= 0:
                    logger.info("Total Number of Processes Running :{0} ,  {1}".format(proc_count, diff))
                else:
                    logger.info("Total Number of Processes Running :{0} ,  +{1}".format(proc_count, diff))
     
            else:
                logger.info("Total Number of Processes Running :{}".format(proc_count))
        
        # write the disk utilization of /var or any errors to the log.
        pcent=diskUsage()
        if pcent is None:
            logger.error("Failed to retrieve information from host {}".format(sys.argv[1]))
        else:
            pcentList.append(pcent)
            if len(pcentList) >= 2:
                pcentList = pcentList[-2:]
                diffpct = int(pcentList[0] - pcentList[1])
                logger.info("Disk space used % of /var :{0}% , and the difference is {1}%".format(pcent, diffpct))
            else:
                logger.info("Disk space used % of /var :{0}%".format(pcent))
        # Parse the syslog
        logparse(logFile)
        # Sleep for the mentioned time
        time.sleep(int(sys.argv[4]))



