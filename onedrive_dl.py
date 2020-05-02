import requests
import wget
import os
import base64

#Covers20K
#https://1drv.ms/u/s!AocykQAvhWc9ax_8RRkxKELRnSs?e=Z443ZC
#Depois que acessa o endereço mostradi é:
#https://onedrive.live.com/?authkey=%21AB%5F8RRkxKELRnSs&id=3D67852F00913287%21107&cid=3D67852F00913287

#Instruções em: https://stackoverflow.com/questions/40454101/access-publicly-shared-onedrive-folder-via-api
#To convert this URL into the API, you first base64 encode the URL and append u! (em https://base64.guru/standards/base64url/encode)
#https://1drv.ms/u/s!AocykQAvhWc9ax_8RRkxKELRnSs?e=Z443ZC
#Convertido (e com u! na frente) vira:
#u!aHR0cHM6Ly8xZHJ2Lm1zL3UvcyFBb2N5a1FBdmhXYzlheF84UlJreEtFTFJuU3M_ZT1aNDQzWkM

# Usando encoder base64 do python:
#u!aHR0cHM6Ly8xZHJ2Lm1zL3UvcyFBb2N5a1FBdmhXYzlheF84UlJreEtFTFJuU3M_ZT1aNDQzWkM=

#Now you can use this URL as the sharing token, and expand children and thumbnails:
#https://api.onedrive.com/v1.0/shares/<COLOQUE A URL EM BASE64 COM O u! NO INICIO AQUI>/root?expand=children
#https://api.onedrive.com/v1.0/shares/u!aHR0cHM6Ly8xZHJ2Lm1zL3UvcyFBb2N5a1FBdmhXYzlheF84UlJreEtFTFJuU3M_ZT1aNDQzWkM/root?expand=children

#Para ver arquivos de uma pasta de nome "10":
#https://api.onedrive.com/v1.0/shares/u!aHR0cHM6Ly8xZHJ2Lm1zL3UvcyFBb2N5a1FBdmhXYzlheF84UlJreEtFTFJuU3M_ZT1aNDQzWkM/root:/10:/children

shared_url = 'https://1drv.ms/u/s!AocykQAvhWc9ax_8RRkxKELRnSs?e=Z443ZC'
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
child_count = data["folder"]["childCount"]  # 4
children = data["children"]  # de 0 a child_count-1
print("\nBaixando arquivos de %d pastas"%(child_count))
for i in range(child_count):
	"""
	>>> children[0].keys()
	dict_keys(['cTag', 'createdBy', 'webUrl', 'createdDateTime', 'size', 'lastModifiedBy', 'parentReference', 'eTag', 'lastModifiedDateTime', 'name', 'reactions', 'fileSystemInfo', 'id', 'folder'])
	"""
	"""
	>>> children[0]["name"]
	'1'
	"""
	"""
	>>> children[0]["webUrl"]
	'https://1drv.ms/f/s!AocykQAvhWc9bB_8RRkxKELRnSs'
	"""

	#https://api.onedrive.com/v1.0/shares/u!aHR0cHM6Ly8xZHJ2Lm1zL3UvcyFBb2N5a1FBdmhXYzlheF84UlJreEtFTFJuU3M_ZT1aNDQzWkM/root:/10:/children
	#str_child = ":/10:/children"
	folder_name = children[i]["name"]
	str_child = ":/"+folder_name+":/children"
	url = url_base+str_child
	mychild = requests.get(url)
	dchild = mychild.json()
	"""
	f = open("out_child.txt","w")
	print(json.dumps(dchild, indent=2), file=f)
	f.close()
	>>> dchild.keys()
	dict_keys(['@odata.count', 'value', '@odata.context'])
	"""
	nfiles = dchild['@odata.count']  #8
	if not os.path.exists(folder_name):
		os.mkdir(folder_name)
	print("\nBaixando %d arquivos da pasta %s"%(nfiles, folder_name))
	for j in range(nfiles):
		"""
		>>> dchild['value'][0].keys()
		dict_keys(['cTag', 'createdBy', 'webUrl', 'createdDateTime', 'reactions', 'lastModifiedBy', 'parentReference', 'shared', 'eTag', 'size', 'file', '@content.downloadUrl', 'name', 'lastModifiedDateTime', 'fileSystemInfo', 'id'])
		"""
		# Alternativa requests
		#fname = dchild['value'][j]['name']
		#fsize = dchild['value'][j]['size']
		#dl_url = dchild['value'][j]['@content.downloadUrl']
		#fcontent = requests.get(dl_url, allow_redirects=True)
		#tamanho_recebido = len(fcontent.content)
		#disposicao_conteudo = fcontent.headers['Content-Disposition']
		"""
		>>> disposicao_conteudo
		'attachment; filename="19629.h5"'
		"""
		#open(fname, 'wb').write(fcontent.content)


		# Alternativa wget - funcionou
		#import wget
		fname = dchild['value'][j]['name']
		fsize = dchild['value'][j]['size']
		dl_url = dchild['value'][j]['@content.downloadUrl']
		out_path_file_name = folder_name+"/"+fname
		if os.path.exists(out_path_file_name):
			print("Arquivo %s ja baixado. Pulando..."%out_path_file_name)
		else:
			print("\nBaixando arquivo %s, com %d bytes na pasta %s"%(fname, fsize, folder_name))
			fname_dl = wget.download(dl_url,out=out_path_file_name)


