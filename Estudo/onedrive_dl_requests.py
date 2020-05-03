import requests

#https://1drv.ms/b/s!AhVyj6iuwGZbsme81HEqt3qr0tQy?e=apsjsq
# A partir do embed, generate html code
#<iframe src="https://onedrive.live.com/embed?cid=5B66C0AEA88F7215&resid=5B66C0AEA88F7215%216503&authkey=AJUchBdIfDFYL1A&em=2" width="476" height="288" frameborder="0" scrolling="no"></iframe>
#basta trocar o embed por download e temos a URL a usar:
#https://onedrive.live.com/download?cid=5B66C0AEA88F7215&resid=5B66C0AEA88F7215%216503&authkey=AJUchBdIfDFYL1A&em=2

# Outro arquivo
#<iframe src="https://onedrive.live.com/embed?cid=5B66C0AEA88F7215&resid=5B66C0AEA88F7215%216501&authkey=ANUVUf-Na5_ZhZE" width="98" height="120" frameborder="0" scrolling="no"></iframe>
#https://onedrive.live.com/download?cid=5B66C0AEA88F7215&resid=5B66C0AEA88F7215%216501&authkey=ANUVUf-Na5_ZhZE

#url_base = "https://1drv.ms/b/s!AhVyj6iuwGZbsme81HEqt3qr0tQy?e=apsjsq"
#url_base = "https://onedrive.live.com/download?cid=5B66C0AEA88F7215&resid=5B66C0AEA88F7215%216503&authkey=AJUchBdIfDFYL1A&em=2"
url_base= "https://onedrive.live.com/download?cid=5B66C0AEA88F7215&resid=5B66C0AEA88F7215%216501&authkey=ANUVUf-Na5_ZhZE"
dl_str = "&download=1"
url = url_base+dl_str

myfile = requests.get(url_base, allow_redirects=True)
tamanho = myfile.headers['Content-Length']
tamanho_recebido = len(myfile.content)
disposicao_conteudo = myfile.headers['Content-Disposition']
#"attachment; filename*=UTF-8''Projeto%20NB%20IoT%20-%20Itajuba.pdf"
fname = disposicao_conteudo.split("''")[1].replace("%20"," ")
#OU
fname = disposicao_conteudo.split("filename=")[1].replace("%20"," ")

outfile = "baixado3.pdf"

#open('c:/users/LikeGeeks/documents/hello.pdf', 'wb').write(myfile.content)
open(outfile, 'wb').write(myfile.content)


#Com wget - não esta funcionando para um arquivo
import wget
url_base = "https://onedrive.live.com/download?cid=5B66C0AEA88F7215&resid=5B66C0AEA88F7215%216503&authkey=AJUchBdIfDFYL1A&em=2"
outfile2 = "baixado4.txt"
myfile2 = wget.download(url_base,out=outfile2)
