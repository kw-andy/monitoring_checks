# Healthcheck (MAJ)



Projet déployant un système de healthcheck des services web hébergés sur un cluster Kubernetes sur lequel Traefik est utilisé comme reverse proxy web centralisé et configuré via des CRD IngressRoute définies par service.


## Objectifs

- Être alerté en cas d'indisponibilité d'un ou plusieurs services
- Ne pas à avoir à configurer manuellement le système (ajout ou suppression d'un service à surveiller)


## Solution

- Utilisation de l'outil [Cabourotte](https://github.com/mcorbin/cabourotte) pour exécuter les healtchecks
- Monitorer Cabourotte via Prometheus
- Configuration d'une alerte via Grafana basée sur les métriques Prometheus
- Mise à jour automatique via un script plannifié de la liste des healtchecks à exécuter par Cabourotte en fonction des services web déployés dans le cluster Kubernetes

### Script plannifié de mise à jour automatique de Cabourotte

#### Principe

- Lister les services web déployés dans Kubernetes
- Lister les healthchecks configurés dans Cabourotte
- Créer les healthchecks manquants
- Supprimer les healtchecks des services n'étant pas déployé dans Kubernetes

# pour faire tourner cabourotte en local

#exemple pour ajouter des healthchecks, en dur dans le fichier yaml: https://gitlab.com/mlf-cloud/infra/eks-cluster/-/blob/op_task_1597/ADDONS/Monitoring/healthcheks/base/cabourotte.yaml

#pour faire tourner cabourotte en utilisant docker
#utiliser la v8.0, la v9.0 pourrait demander un certificat
docker run -v /home/user/folder_of_my_project/cabourotte/cabourotte.yaml:/cabourotte.yaml -p 9013:9013 mcorbin/cabourotte:v0.8.0

#pour visualiser les logs
docker logs -f --tail 10 container_name