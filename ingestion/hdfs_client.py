from hdfs import InsecureClient

# connect to namenode
client = InsecureClient("http://namenode:9870", user="root")

def upload_to_hdfs(local_path, hdfs_path):

    parent = hdfs_path.rsplit("/", 1)[0]

    client.makedirs(parent)

    if client.status(hdfs_path, strict=False):
        return

    client.upload(
        hdfs_path,
        local_path,
        overwrite=False
    )
# def upload_to_hdfs(local_path, hdfs_path):
#     client.makedirs(hdfs_path.rsplit("/", 1)[0])
#     client.upload(hdfs_path, local_path, overwrite=True)