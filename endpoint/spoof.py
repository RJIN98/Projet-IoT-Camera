#!/usr/bin/env python3

import smtplib
from sys import argv


if __name__ == "__main__":
    to_email =   argv[1] if len(argv) > 1 else input("Adresse vers laquelle envoyer les spoof emails : ")
    to_name = argv[2] if len(argv) > 2 else input("Nom du destinataire : ")

    print(f"Dest email : {to_email}\nDest name: {to_name}")


    while input("Continue ?[O/n]") not in ("", "O"):

        to_email = input("Adresse vers laquelle envoyer les spoof emails : ")
        to_name = input("Nom du destinataire : ")

        print(f"Dest email : {to_email}\nDest name: {to_name}")

    content = "Phishing email"


    #server = smtplib.SMTP("smtp.gmail.com", 587)
    server = smtplib.SMTP("localhost", 25)
    #server.starttls()
    #username= input("entrez votre adresse mail:")
    #password = input("Entrez votre mdp :")
    #server.login(username, password)
    fake_from = f"patron@cisco.com"
    fake_name = f"patron de cisco.com"
    username = fake_name
    subject = f"Phishing from cisco.com"
    message = f"From: {fake_name} <{fake_from}>\nTo: {to_name} <{to_email}>\nSubject: {subject}\n\n{content}"
    server.sendmail(fake_from, to_email, message.encode())
    server.close()
    quit()
    
    for ligne in open("allAllFile.txt"):
        domain = ligne[:-1]
        print(domain)
        fake_from = f"patron@{domain}"
        fake_name = f"patron de {domain}"
        username = fake_name

        subject = f"Phishing from {domain}"

        message = f"From: {fake_name} <{fake_from}>\nTo: {to_name} <{to_email}>\nSubject: {subject}\n\n{content}"

        server.sendmail(fake_from, to_email, message.encode())
        if input("Continue ?[O/n]") not in ("", "O"):
            break

    server.close()
