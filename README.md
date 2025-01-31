# Documentation du Système RAG basé sur des Microservices

## Table des Matières
- [1. Introduction](#1-introduction)
- [2. Objectif Général](#2-objectif-général)
- [3. Architecture du Système](#3-architecture-du-système)
  - [3.1 Vue d'ensemble](#31-vue-densemble)
  - [3.2 Architecture Basique RAG](#32-architecture-basique-rag)
- [4. Composants Clés du Projet](#4-composants-clés-du-projet)
  - [4.1 Service d'Indexation](#41-service-dindexation)
  - [4.2 Service Agent Conversationnel](#42-service-agent-conversationnel)
  - [4.3 Service Média](#43-service-média)
  - [4.4 Composant Partagé](#44-composant-partagé)
  - [4.5 Déploiement Kubernetes](#45-déploiement-kubernetes)
- [5. Déploiement et Tests](#5-déploiement-et-tests)
  - [5.1 Déploiement avec Docker Hub et Kubernetes](#51-déploiement-avec-docker-hub-et-kubernetes)
  - [5.2 Vérification des Services](#52-vérification-des-services)
  - [5.3 Exposition des Services](#53-exposition-des-services)
- [6. Interaction des Services](#6-interaction-des-services)
  - [6.1 Détails du Flux d’Interaction](#61-détails-du-flux-dinteraction)
- [7. Conclusion](#7-conclusion)

---

## 1. Introduction

Ce document décrit une plateforme modulaire d’indexation et d’interrogation de données multimodales, intégrant des modèles d’intelligence artificielle pour la recherche sémantique et la génération de réponses.

---

## 2. Objectif Général

Le projet repose sur FastAPI, ChromaDB et LlamaIndex pour traiter, indexer et interroger divers types de données textuelles et audiovisuelles. Il permet une recherche sémantique efficace et un accès structuré aux connaissances.

---

## 3. Architecture du Système

### 3.1 Vue d’Ensemble

Le système repose sur trois microservices principaux et un module partagé :
- **Chat Agent Service** : Fournit un agent conversationnel.
- **Indexing Service** : Service d’indexation de documents.
- **Media Service** : Traitement multimédia.
- **Composant Partagé** : Gestion des index vectoriels.

### 3.2 Architecture RAG
```plaintext
                           ┌──────────────────────────┐
                           │  Client Utilisateur      │
                           └──────────┬──────────────┘
                                      │
                        ┌─────────────▼──────────────┐
                        │  Chat Agent Service        │
                        │  (chat_agent_service.py)   │
                        └───────┬───────────┬───────┘
                                │           │
                  ┌─────────────▼───┐    ┌──▼───────────────┐
                  │Indexing Service │    │ Media Service    │
                  │(indexing_serv.) │    │ (media_service)  │
                  └─────────────┬───┘    └──┬───────────────┘
                                │           │
                       ┌────────▼───────────▼───────┐
                       │  Stockage et Index Vector. │
                       │  (vector_index_utils.py)  │
                       └───────────────────────────┘
```

---

## 4. Composants Clés du Projet

### 4.1 🔍 Service d’Indexation (indexing_service)
- **Rôle** : Indexation de fichiers texte (.txt, .md), PDF et autres sources.
- **Moteur** : LlamaIndex pour générer des embeddings vectoriels.
- **API** :
  - `/indexing/ingest` → Upload et indexation d’un document.
  - `/documents` → Liste des documents indexés.

### 4.2 🤖 Service Agent Conversationnel (chat_agent_service)
- **Rôle** : Répond aux requêtes utilisateurs via un agent ReAct basé sur GPT-3.5.
- **Moteur** : OpenAI GPT-3.5 + LlamaIndex.
- **API** :
  - `/chat/chat-with-agent` → Envoi d’une requête à l’agent IA.

### 4.3 📽️ Service Média (media_service)
- **Rôle** : Extraction et indexation de contenu multimédia.
- **API** :
  - `/media/process-and-index` → Traitement d’une vidéo.
  - `/media/process-and-index-image` → Analyse et indexation d’une image.

### 4.4 🗄️ Composant Partagé (vector_index_utils)
- **Rôle** : Gestion centralisée de l’index vectoriel.
- **Moteur** : LlamaIndex + OpenAI.

### 4.5 📦 Déploiement Kubernetes
- **Objectif** : Conteneurisation et orchestration des services.
- **Composants** :
  - Déploiements Kubernetes.
  - Volume partagé pour stocker les fichiers indexés.

---

## 5. Déploiement et Tests

### 5.1 Déploiement avec Docker Hub et Kubernetes
- **Cloner le dépôt** :
```sh
git clone https://github.com/JEMALIACHRAF/Note-Gestion.git
cd YOUR_REPO/k8s
```
- **Appliquer la configuration du volume** :
```sh
kubectl apply -f shared-volume.yml
```
- **Pull des images Docker** :
```sh
docker pull ashraf081/indexing-service:latest
docker pull ashraf081/media-service:latest
docker pull ashraf081/chat-agent-service:latest
```
- **Déploiement Kubernetes** :
```sh
kubectl apply -f indexing-service-deployment.yml
kubectl apply -f media-service-deployment.yml
kubectl apply -f chat-agent-service-deployment.yml
```

### 5.2 Vérification des Services
```sh
kubectl get pods
kubectl get services
```

### 5.3 Exposition des Services
```sh
kubectl port-forward svc/indexing-service 8001:8001
kubectl port-forward svc/media-service 8002:8002
kubectl port-forward svc/chat-agent-service 8003:8003
```

---

## 6. Interaction des Services

### 6.1 Détails du Flux d’Interaction
1. **Indexation** : Documents soumis via `Indexing Service` → Vectorisation.
2. **Traitement Multimédia** : Extraction et transcription.
3. **Requête Utilisateur** : Analyse et récupération des documents pertinents.
4. **Génération de Réponse** : LLM enrichit la réponse avec du contexte.

---

## 7. Conclusion

Le projet combine NLP avancé, agents conversationnels et traitement multimédia pour fournir un moteur de recherche sémantique puissant, scalable et structuré.

🚀 **Votre application est maintenant prête à être utilisée !** 🎉
