#!/usr/bin/python3
from os import getenv
import logging
import requests
import subprocess
from http.client import HTTPConnection
import json
import re
import sys

# export CABOUROTTE_URL='127.0.0.1:9013'
# export KUB_CONTEXT='akwok-client-stuff-dev'


CABOUROTTE_URL = getenv("CABOUROTTE_URL")
KUB_CONTEXT = getenv("KUB_CONTEXT")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# for debugging
# kubectl --context akwok-client-stuff-dev -n kub-acme get -o=custom-columns=svc:.spec.routes[0].match ingressroute kub-acme-acmewordpress

# cette fonction est pour récupérer les ingress routes
def kubectl_ingress():
    logging.info(f"Start kubectl_ingress with {KUB_CONTEXT}")
    # cette partie allant jusqu'à outlist_final permet d'avoir une pair, name et namespace
    bashCmdNamespace = [
        "kubectl",
        "--context",
        f"{KUB_CONTEXT}",
        "get",
        "--all-namespaces",
        "ingressroutes",
    ]
    # vérifie s'il y'a erreur. Si oui, la fonction s'arrête et retourne l'erreur
    bashresults = subprocess.run(bashCmdNamespace, capture_output=True)
    # print(bashresults)
    if bashresults.returncode == 1:
        ERR = bashresults.stderr.decode("utf-8")
        logging.info(f"Error with kubectl_ingress: {ERR}")
        return logging.info(f"Exit 1")
    logging.info(f"End kubectl_ingress with {KUB_CONTEXT}. Exit 0")

    return bashresults.stdout.decode("utf-8")


# cette fonction est pour nettoyer les ingress routes, une fois récupérés
# faire obtenir en fin, des sous listes contenant, le NAMESPACE et le NAME
def ingress_cleaning(kubectl_ingress):
    logging.info(f"Start ingress_cleaning with {KUB_CONTEXT}")
    output = kubectl_ingress
    outwithoutspace = re.sub("\s+", " ", output)
    outlist = outwithoutspace.split(" ")
    outlist = outlist[3:]
    # etape supprimant les valeurs vides dans la liste
    outlist = [val for val in outlist if val]
    outlist_final = [vale for pos, vale in enumerate(outlist) if (pos + 1) % 3 != 0]
    # detail
    compos_list = [outlist_final[x : x + 2] for x in range(0, len(outlist_final), 2)]
    logging.info(f"End kubectl_ingress with {KUB_CONTEXT}. Exit 0")
    return compos_list


# cette fonction permet d'obtenir la partie URL brut
# et ajoute aux sous listes contenant, le NAMESPACE et le NAME, l'URL
def kubectl_routes(ingress_cleaning):
    logging.info(f"Start kubectl_routes with {KUB_CONTEXT}")
    compos_list = ingress_cleaning
    for value in compos_list:
        bashCmdIngress = [
            "kubectl",
            "--context",
            f"{KUB_CONTEXT}",
            "-n",
            f"{value[0]}",
            "get",
            "-o=custom-columns=:.spec.routes[0].match",
            "ingressroute",
            f"{value[1]}",
        ]
        bashingress = subprocess.run(bashCmdIngress, capture_output=True)
        if bashingress.returncode == 1:
            ERR = bashingress.stderr.decode("utf-8")
            logging.info("Error with  kubectl_routes {stderr}")
        output_yaml = bashingress.stdout.decode("utf-8")
        value.append(output_yaml)
    return compos_list


# cette fonction permet de nettoyer l'URL
# et ajoute aux sous listes contenant, le NAMESPACE et le NAME, l'URL
# j'ai ajouté les régles de gestion, en terme de nettoyage
def routes_cleaning(kubectl_routes):
    logging.info(f"Start routes_cleaning with {KUB_CONTEXT}")
    output_yaml = kubectl_routes
    for value in output_yaml:
        '''
        pour là où il y'a plus d'une URL et séparée par des valeurs séparées 
        soit par \ , ou | ou \n ainsi que ` et Host (comme mot)
        '''
        if re.findall("\,|\&|\|", value[2]):
            sep = re.findall("\,|\&|\|", value[2])[0]
            # on elimine la partie après le séparateur, sep
            output_url = value[2].split(sep, 1)[0]
            # on enleve le début de la string, la partie avec Host\(
            output_url = re.sub("Host\(", "", output_url)
            # on enleve les backtices
            output_url = re.sub("`", "", output_url)
            # on enleve les \n
            output_url = output_url.replace("\n", " ")
        # Si le cas n'est pas celui du if
        # on s'attaque aux URLs uniques, avec la même séquence
        else:
            output_url = re.sub("Host\(", "", value[2])
            output_url = re.sub("`", "", output_url)
            output_url = output_url.replace("\n", " ")
        # enfin, si un ) est trouvé, on l'enlève
        if re.findall("\)", output_url):
            output_url = re.sub("\)", "", output_url)
        # toutes les urls ont leurs espaces enlevés
        output_url = output_url.strip()
        # on remplace la deuxième valeur de chaque sous-liste
        # par l'url nettoyé
        value[2] = output_url
    logging.info(f"Stop routes_cleaning with {KUB_CONTEXT}. Exit 0")
    return output_yaml


# cette fonction permet de lister les services déjà déployées sous Cabourotte
def healthchecks_list():
    logging.info(f"Start healthchecks_list with {KUB_CONTEXT}")
    output = requests.get(f"http://{CABOUROTTE_URL}/healthcheck")
    # récuperation des healthchecks de cabourotte avec le name et l'url dans 1 liste
    output = output.text[1:-2]
    json_dict = json.loads("[" + output.replace("}{", "},{") + "]")
    name_target_lst = [
        [json_dict[key]["name"], json_dict[key]["target"]]
        for key, val in enumerate(json_dict)
    ]
    logging.info(f"Stop healthchecks_list with {KUB_CONTEXT}. Exit 0")
    return name_target_lst


# cette fonction permet de rajouter les services non
# monitorées, qui existent dans le cluster
def add_healthcheck(webservices, healthchecks):
    logging.info(f"Start add_healthcheck with {KUB_CONTEXT}")
    headers = {
        "Content-Type": "application/json",
    }
    healthinars_names = {vale[0] for vale in healthchecks}
    ah_return_code = []
    for subl in webservices:
        if subl[0] not in healthinars_names:
            data = f'{{"name":"{subl[0]}","description":"{subl[0]}","target":"{subl[2]}","interval":"5s","timeout": "3s","port":443,"protocol":"https","valid-status":[200]}}'
            results = requests.post(
                f"http://{CABOUROTTE_URL}/healthcheck/http", headers=headers, data=data
            )
            results.text
            ah_return_code.append(str(results.status_code) + ":" + data)
            # print(ah_return_code)
    ah_return_code = str(ah_return_code).strip("[]")
    ah_return_code = ah_return_code.replace("'", "")
    logging.info(f"Stop add_healthcheck with {KUB_CONTEXT}. Exit 0")
    return ah_return_code


# cette fonction permet de supprimer les services
# encore monitorées mais qui n'existent plus dans le cluster
def remove_healthcheck(webservices, healthchecks):
    logging.info(f"Start remove_healthcheck with {KUB_CONTEXT}")
    webinars_names = {vale[0] for vale in webservices}
    rh_return_code = []
    for subl in healthchecks:
        if subl[0] not in webinars_names:
            data = subl[0]
            results = requests.delete(f"http://{CABOUROTTE_URL}/healthcheck/{data}")
            results.text
            rh_return_code.append(str(results.status_code) + ":" + results.text)
    rh_return_code = ",".join(rh_return_code)
    rh_return_code = rh_return_code.replace("\n", "")
    logging.info(f"Stop remove_healthcheck with {KUB_CONTEXT}. Exit 0")
    return rh_return_code


if __name__ == "__main__":
    kubectl_ingress = kubectl_ingress()
    ingress_cleaning = ingress_cleaning(kubectl_ingress)
    kubectl_routes = kubectl_routes(ingress_cleaning)
    webservices = routes_cleaning(kubectl_routes)
    healthchecks = healthchecks_list()
    add_healthcheck(webservices, healthchecks)
    remove_healthcheck(webservices, healthchecks)
