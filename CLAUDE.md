# Instructions pour Claude

## Règles Git

- **TOUJOURS** demander la permission avant de faire un `git push`
- Ne jamais pousser automatiquement les modifications vers GitHub
- Attendre l'autorisation explicite de l'utilisateur avant tout push

## Workflow Git recommandé

1. Faire les modifications nécessaires
2. Créer un commit avec un message descriptif
3. **DEMANDER** : "Puis-je pousser ces modifications vers GitHub ?"
4. Attendre la réponse de l'utilisateur
5. Si autorisé, alors exécuter `git push`

## Exemple

```
Claude: J'ai créé un commit avec les modifications. Puis-je pousser ces changements vers GitHub ?
Utilisateur: Oui, tu peux push
Claude: [Exécute git push]
```