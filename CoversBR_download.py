"""
CoversBR_download.py
Developed by Atila Xavier, 01/05/2020, as a tool to download all feature files of the CoversBR database (HDF5 format)
shared_url = 'https://1drv.ms/u/s!AocykQAvhWc9ax_8RRkxKELRnSs?e=Z443ZC'
Files are downloaded from a public repository, and will be saved with the same structure as the source, on the folder where this script is executed.
Structure is:
.
	<work_id 1>
		<track_id A>.h5
		<track_id B>.h5
		.
		.
		<track_id N>.h5
	<work_id 2>
		<track_id X>.h5
		<track_id Y>.h5
		.
		.

Writen for Python 3.x
Depends on the libraries:
"""
import requests
import wget
import os
import base64
import argparse


def Dl_file(s, fchild, local_folder_name):
	fname = fchild['name']
	fsize = fchild['size']
	dl_url = fchild['@content.downloadUrl']
	out_path_file_name = local_folder_name+"/"+fname
	if os.path.exists(out_path_file_name):
		print("File %s already downloaded. Skipping..."%out_path_file_name)
	else:
		print("Downloading file %s, with %d bytes, to folder %s"%(fname, fsize, local_folder_name))
		# Using wget (not working with some file/folder names:
		"""
		fname_dl = wget.download(dl_url,out=out_path_file_name)
		print("\n")
		"""
		# Using requests:
		fcontent = s.get(dl_url, allow_redirects=True)
		received_size = len(fcontent.content)
		if received_size == fsize:
			open(out_path_file_name, 'wb').write(fcontent.content)
			print(" OK - %d bytes received"%received_size)
		else:
			print("Error downloading %s: expected %d bytes, received %d bytes"%(out_path_file_name, fsize, received_size))

def Dl_child(s, child, remote_folder_name, local_folder):
	"""
	>>> children[0].keys()
	dict_keys(['cTag', 'createdBy', 'webUrl', 'createdDateTime', 'size', 'lastModifiedBy', 'parentReference', 'eTag', 'lastModifiedDateTime', 'name', 'reactions', 'fileSystemInfo', 'id', 'folder'])
	"""
	folder_name = child["name"]
	remote_folder_name = remote_folder_name + "/" + folder_name
	str_child = ":"+remote_folder_name+":/children"
	url = url_base+str_child
	mychild = s.get(url)
	dchild = mychild.json()
	"""
	To see a readale print of JSON
	f = open("out_child.txt","w")
	print(json.dumps(dchild, indent=2), file=f)
	f.close()
	>>> dchild.keys()
	dict_keys(['@odata.count', 'value', '@odata.context'])
	"""
	nfiles = dchild['@odata.count']  #8
	local_folder_name = local_folder+"/"+folder_name
	if not os.path.exists(local_folder_name):
		print("Creating folder %s"%local_folder_name)
		os.mkdir(local_folder_name)
	print("Downloading %d file(s) from folder %s"%(nfiles, remote_folder_name))
	for fchild in dchild["value"]:
		"""
		>>> dchild['value'][0].keys()
		dict_keys(['cTag', 'createdBy', 'webUrl', 'createdDateTime', 'reactions', 'lastModifiedBy', 'parentReference', 'shared', 'eTag', 'size', 'file', '@content.downloadUrl', 'name', 'lastModifiedDateTime', 'fileSystemInfo', 'id'])
		For files, there is a key "file"
		OR
		>>> dchild["value"][0].keys()
		dict_keys(['createdDateTime', 'lastModifiedBy', 'id', 'size', 'cTag', 'reactions', 'parentReference', 'createdBy', 'fileSystemInfo', 'shared', 'name', 'folder', 'webUrl', 'lastModifiedDateTime', 'eTag'])
		For folders, there is a key "folder"
		"""
		if "folder" in fchild:
			Dl_child(s, fchild, remote_folder_name, local_folder_name)
		else:
			Dl_file(s, fchild, local_folder_name)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description=
				"Downloads all files from a publicly shared onedrive folder via api \
				to the current folder, replicating the OneDrive folder structure.",
				formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument("-url", action="store",  default = "https://1drv.ms/u/s!AocykQAvhWc9ghh04i3ZpSy6jHsf?e=HutI4W",
						dest="shared_url", 
						help="OneDrive shared URL.")
#CoversBR benchmark
#https://1drv.ms/u/s!AocykQAvhWc9ghh04i3ZpSy6jHsf?e=HutI4W
#Covers20k
#https://1drv.ms/u/s!AocykQAvhWc9ax_8RRkxKELRnSs?e=Z443ZC
	args_main = parser.parse_args()
	shared_url = args_main.shared_url
	shared_url_b64 = base64.urlsafe_b64encode(shared_url.encode('ascii')).decode('ascii')
	url_base = "https://api.onedrive.com/v1.0/shares/u!"+shared_url_b64	+"/root"
	#url_base = "https://api.onedrive.com/v1.0/shares/u!aHR0cHM6Ly8xZHJ2Lm1zL3UvcyFBb2N5a1FBdmhXYzlheF84UlJreEtFTFJuU3M_ZT1aNDQzWkM/root"
	str_root= "?expand=children"
	url = url_base+str_root
	headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36',
    'Content-Type': 'text/html',
	'connection': 'keep-alive',
	}
	session = requests.Session()
	myroot = session.get(url, headers = headers)
	dt = data = myroot.json()
	while "children@odata.nextLink" in dt:
		r = session.get(dt['children@odata.nextLink'], headers = headers)
		dt = r.json()
		data['children'].extend(dt['value'])
	"""
	>>> data.keys()
	dict_keys(['cTag', 'createdBy', 'webUrl', 'createdDateTime', 'size', 'lastModifiedBy', 'parentReference', 'children', '@odata.context', 'shared', 'eTag', 'children@odata.count', 'lastModifiedDateTime', 'name', 'children@odata.context', 'reactions', 'fileSystemInfo', 'id', 'folder'])
	
	dict_keys(['id', 'parentReference', 'children', 'lastModifiedBy', 'children@odata.count', 'shared', 'webUrl', 'lastModifiedDateTime', 'children@odata.nextLink', 'reactions', 'createdDateTime', 'children@odata.context', 'cTag', 'eTag', 'name', 'fileSystemInfo', 'size', '@odata.context', 'folder', 'createdBy'])
	>>> data['children@odata.nextLink']
	"https://api.onedrive.com/v1.0/shares('u!aHR0cHM6Ly8xZHJ2Lm1zL3UvcyFBb2N5a1FBdmhXYzlnaGgwNGkzWnBTeTZqSHNmP2U9SHV0STRX')/items('3D67852F00913287!280')/children/?$skiptoken=MjAx"
	
	 myroot2 = s.get(data['children@odata.nextLink'], headers = headers, stream=True)
	data2 = myroot2.json() 
	>>> data2.keys()
	dict_keys(['value', '@odata.context', '@odata.nextLink', '@odata.count'])
	>>> data2['@odata.count']
	9184
	>>> data2['@odata.nextLink']
	"https://api.onedrive.com/v1.0/shares('u!aHR0cHM6Ly8xZHJ2Lm1zL3UvcyFBb2N5a1FBdmhXYzlnaGgwNGkzWnBTeTZqSHNmP2U9SHV0STRX')/items('3D67852F00913287!280')/children/?$skiptoken=NDAx"
	>>> data['children'][0].keys()
	dict_keys(['id', 'parentReference', 'cTag', 'lastModifiedBy', 'webUrl', 'lastModifiedDateTime', 'reactions', 'createdDateTime', 'createdBy', 'eTag', 'name', 'fileSystemInfo', 'size', 'folder'])
	>>> data2['value'][0].keys()
	dict_keys(['id', 'parentReference', 'cTag', 'lastModifiedBy', 'shared', 'webUrl', 'lastModifiedDateTime', 'reactions', 'createdDateTime', 'createdBy', 'eTag', 'name', 'fileSystemInfo', 'size', 'folder'])
	data['children'].extend(data2['value'])
	"""
	child_count = data["folder"]["childCount"] 
	children = data["children"] 
	folder_name = ""
	local_folder_name = "."
	print("Downloading %d files/folders from %s"%(child_count, shared_url))
	dwonloaded_folders_count = 0
	for child in data["children"]:
		if "folder" in child:
			Dl_child(session, child, folder_name, local_folder_name)
			dwonloaded_folders_count += 1
		else:
			Dl_file(session, child, local_folder_name)
	print("Finished downloading %d folders"%dwonloaded_folders_count)