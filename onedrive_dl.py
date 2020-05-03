<<<<<<< HEAD
#!/usr/bin/env python
"""
Routine to download all files from a publicly shared onedrive folder via shares REST API (https://dev.onedrive.com/shares/shares.htm)
Writeen by Atila Xavier, May/2020
Thanks to instructions at https://stackoverflow.com/questions/40454101/access-publicly-shared-onedrive-folder-via-api from Ryan Gregg (https://stackoverflow.com/users/3491656/ryan-gregg) and Brad (https://stackoverflow.com/users/3570009/brad)

"""

import requests
import wget
import os
import base64
import argparse

#Example shared folder: CoversBR
#https://1drv.ms/u/s!AocykQAvhWc9ax_8RRkxKELRnSs?e=Z443ZC
#Depois que acessa o endereço mostrado é:
#https://onedrive.live.com/?authkey=%21AB%5F8RRkxKELRnSs&id=3D67852F00913287%21107&cid=3D67852F00913287

#Another example shared folder with recursive folders
#https://1drv.ms/u/s!AhVyj6iuwGZbsnQSZjlOPb_Y-t5t?e=IMUqpd

#Instructions at: https://stackoverflow.com/questions/40454101/access-publicly-shared-onedrive-folder-via-api
#To convert this URL into the API, you first base64 encode the URL and append u! (em https://base64.guru/standards/base64url/encode)
#https://1drv.ms/u/s!AocykQAvhWc9ax_8RRkxKELRnSs?e=Z443ZC
#Converted (and with u! at the begining) becomes:
#u!aHR0cHM6Ly8xZHJ2Lm1zL3UvcyFBb2N5a1FBdmhXYzlheF84UlJreEtFTFJuU3M_ZT1aNDQzWkM

# Using base64 python´s encoder :
#u!aHR0cHM6Ly8xZHJ2Lm1zL3UvcyFBb2N5a1FBdmhXYzlheF84UlJreEtFTFJuU3M_ZT1aNDQzWkM=

#Now you can use this URL as the sharing token, and expand children and thumbnails:
#https://api.onedrive.com/v1.0/shares/<COLOQUE A URL EM BASE64 COM O u! NO INICIO AQUI>/root?expand=children
#https://api.onedrive.com/v1.0/shares/u!aHR0cHM6Ly8xZHJ2Lm1zL3UvcyFBb2N5a1FBdmhXYzlheF84UlJreEtFTFJuU3M_ZT1aNDQzWkM/root?expand=children

#To list files from a folder named "10":
#https://api.onedrive.com/v1.0/shares/u!aHR0cHM6Ly8xZHJ2Lm1zL3UvcyFBb2N5a1FBdmhXYzlheF84UlJreEtFTFJuU3M_ZT1aNDQzWkM/root:/10:/children

def Dl_file(fchild, local_folder_name):
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
		fcontent = requests.get(dl_url, allow_redirects=True)
		received_size = len(fcontent.content)
		if received_size == fsize:
			open(out_path_file_name, 'wb').write(fcontent.content)
			print(" OK - %d bytes received"%received_size)
		else:
			print("Error downloading %s: expected %d bytes, received %d bytes"%(out_path_file_name, fsize, received_size))
		

def Dl_child(child, remote_folder_name, local_folder):
	"""
	>>> children[0].keys()
	dict_keys(['cTag', 'createdBy', 'webUrl', 'createdDateTime', 'size', 'lastModifiedBy', 'parentReference', 'eTag', 'lastModifiedDateTime', 'name', 'reactions', 'fileSystemInfo', 'id', 'folder'])
	"""
	folder_name = child["name"]
	remote_folder_name = remote_folder_name + "/" + folder_name
	str_child = ":"+remote_folder_name+":/children"
	url = url_base+str_child
	mychild = requests.get(url)
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
			Dl_child(fchild, remote_folder_name, local_folder_name)
		else:
			Dl_file(fchild, local_folder_name)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description=
				"Downloads all files from a publicly shared onedrive folder via api \
				to the current folder, replicating the OneDrive folder structure.",
				formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument("-url", action="store",  default = "https://1drv.ms/u/s!AocykQAvhWc9ax_8RRkxKELRnSs?e=Z443ZC",
						dest="shared_url", 
						help="OneDrive shared URL.")

	args_main = parser.parse_args()
	shared_url = args_main.shared_url
	shared_url_b64 = base64.urlsafe_b64encode(shared_url.encode('ascii')).decode('ascii')
	url_base = "https://api.onedrive.com/v1.0/shares/u!"+shared_url_b64	+"/root"
	#url_base = "https://api.onedrive.com/v1.0/shares/u!aHR0cHM6Ly8xZHJ2Lm1zL3UvcyFBb2N5a1FBdmhXYzlheF84UlJreEtFTFJuU3M_ZT1aNDQzWkM/root"
	str_root= "?expand=children"
	url = url_base+str_root
	myroot = requests.get(url)
	data = myroot.json()
	"""
	>>> data.keys()
	dict_keys(['cTag', 'createdBy', 'webUrl', 'createdDateTime', 'size', 'lastModifiedBy', 'parentReference', 'children', '@odata.context', 'shared', 'eTag', 'children@odata.count', 'lastModifiedDateTime', 'name', 'children@odata.context', 'reactions', 'fileSystemInfo', 'id', 'folder'])
	"""
	child_count = data["folder"]["childCount"] 
	children = data["children"] 
	folder_name = ""
	local_folder_name = "."
	print("Downloading %d files/folders from %s"%(child_count, shared_url))
	for child in data["children"]:
		if "folder" in child:
			Dl_child(child, folder_name, local_folder_name)
		else:
			Dl_file(child, local_folder_name)


=======
#!/usr/bin/env python
"""
Routine to download all files from a publicly shared onedrive folder via shares REST API (https://dev.onedrive.com/shares/shares.htm)
Writeen by Atila Xavier, May/2020
Thanks to instructions at https://stackoverflow.com/questions/40454101/access-publicly-shared-onedrive-folder-via-api from Ryan Gregg (https://stackoverflow.com/users/3491656/ryan-gregg) and Brad (https://stackoverflow.com/users/3570009/brad)

"""

import requests
import wget
import os
import base64
import argparse

#Example shared folder: CoversBR
#https://1drv.ms/u/s!AocykQAvhWc9ax_8RRkxKELRnSs?e=Z443ZC
#Depois que acessa o endereço mostrado é:
#https://onedrive.live.com/?authkey=%21AB%5F8RRkxKELRnSs&id=3D67852F00913287%21107&cid=3D67852F00913287

#Another example shared folder with recursive folders
#https://1drv.ms/u/s!AhVyj6iuwGZbsnQSZjlOPb_Y-t5t?e=IMUqpd

#Instructions at: https://stackoverflow.com/questions/40454101/access-publicly-shared-onedrive-folder-via-api
#To convert this URL into the API, you first base64 encode the URL and append u! (em https://base64.guru/standards/base64url/encode)
#https://1drv.ms/u/s!AocykQAvhWc9ax_8RRkxKELRnSs?e=Z443ZC
#Converted (and with u! at the begining) becomes:
#u!aHR0cHM6Ly8xZHJ2Lm1zL3UvcyFBb2N5a1FBdmhXYzlheF84UlJreEtFTFJuU3M_ZT1aNDQzWkM

# Using base64 python´s encoder :
#u!aHR0cHM6Ly8xZHJ2Lm1zL3UvcyFBb2N5a1FBdmhXYzlheF84UlJreEtFTFJuU3M_ZT1aNDQzWkM=

#Now you can use this URL as the sharing token, and expand children and thumbnails:
#https://api.onedrive.com/v1.0/shares/<COLOQUE A URL EM BASE64 COM O u! NO INICIO AQUI>/root?expand=children
#https://api.onedrive.com/v1.0/shares/u!aHR0cHM6Ly8xZHJ2Lm1zL3UvcyFBb2N5a1FBdmhXYzlheF84UlJreEtFTFJuU3M_ZT1aNDQzWkM/root?expand=children

#To list files from a folder named "10":
#https://api.onedrive.com/v1.0/shares/u!aHR0cHM6Ly8xZHJ2Lm1zL3UvcyFBb2N5a1FBdmhXYzlheF84UlJreEtFTFJuU3M_ZT1aNDQzWkM/root:/10:/children

def Dl_file(fchild, local_folder_name):
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
		fcontent = requests.get(dl_url, allow_redirects=True)
		received_size = len(fcontent.content)
		if received_size == fsize:
			open(out_path_file_name, 'wb').write(fcontent.content)
			print(" OK - %d bytes received"%received_size)
		else:
			print("Error downloading %s: expected %d bytes, received %d bytes"%(out_path_file_name, fsize, received_size))
		

def Dl_child(child, remote_folder_name, local_folder):
	"""
	>>> children[0].keys()
	dict_keys(['cTag', 'createdBy', 'webUrl', 'createdDateTime', 'size', 'lastModifiedBy', 'parentReference', 'eTag', 'lastModifiedDateTime', 'name', 'reactions', 'fileSystemInfo', 'id', 'folder'])
	"""
	folder_name = child["name"]
	remote_folder_name = remote_folder_name + "/" + folder_name
	str_child = ":"+remote_folder_name+":/children"
	url = url_base+str_child
	mychild = requests.get(url)
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
			Dl_child(fchild, remote_folder_name, local_folder_name)
		else:
			Dl_file(fchild, local_folder_name)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description=
				"Downloads all files from a publicly shared onedrive folder via api \
				to the current folder, replicating the OneDrive folder structure.",
				formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument("-url", action="store",  default = "https://1drv.ms/u/s!AocykQAvhWc9ax_8RRkxKELRnSs?e=Z443ZC",
						dest="shared_url", 
						help="OneDrive shared URL.")

	args_main = parser.parse_args()
	shared_url = args_main.shared_url
	shared_url_b64 = base64.urlsafe_b64encode(shared_url.encode('ascii')).decode('ascii')
	url_base = "https://api.onedrive.com/v1.0/shares/u!"+shared_url_b64	+"/root"
	#url_base = "https://api.onedrive.com/v1.0/shares/u!aHR0cHM6Ly8xZHJ2Lm1zL3UvcyFBb2N5a1FBdmhXYzlheF84UlJreEtFTFJuU3M_ZT1aNDQzWkM/root"
	str_root= "?expand=children"
	url = url_base+str_root
	myroot = requests.get(url)
	data = myroot.json()
	"""
	>>> data.keys()
	dict_keys(['cTag', 'createdBy', 'webUrl', 'createdDateTime', 'size', 'lastModifiedBy', 'parentReference', 'children', '@odata.context', 'shared', 'eTag', 'children@odata.count', 'lastModifiedDateTime', 'name', 'children@odata.context', 'reactions', 'fileSystemInfo', 'id', 'folder'])
	"""
	child_count = data["folder"]["childCount"] 
	children = data["children"] 
	folder_name = ""
	local_folder_name = "."
	print("Downloading %d files/folders from %s"%(child_count, shared_url))
	for child in data["children"]:
		if "folder" in child:
			Dl_child(child, folder_name, local_folder_name)
		else:
			Dl_file(child, local_folder_name)


>>>>>>> e0ec1279326b3d7953d41d8c806c5ea601d5e6ae
