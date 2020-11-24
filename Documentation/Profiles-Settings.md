# Profils & Paramètres


Cura utilise un système de profils superposés. Un aperçu schématique de ce système est présenté dans l'image ci-dessous.

![Machine instance](machine_instance.svg)

## Paramètres


Chacune des entrées de la pile (par exemple, Utilisateur, Qualité, Matériel, etc.) décrit un profil. Lorsque nous voulons savoir quel pourcentage de remplissage doit être utilisé ("infill_sparse_density"), nous demandons simplement à la pile de l'extrudeuse quelle est sa valeur. La pile de l'extrudeuse demandera ensuite à chacun des profils qu'elle possède (en séquence) s'ils ont une valeur pour le paramètre demandé. Le premier profil à donner une réponse définira le résultat.

Une situation un peu plus compliquée se produit lorsque la valeur d'un paramètre est définie par une fonction. Prenons l'exemple suivant. Nous avons un paramètre "foo" dont la valeur est définie par la formule "=bar / 2". Cette valeur est définie dans le profil de qualité de l'extrudeuse de gauche. La valeur de "bar" est définie dans le matériau uniquement et est fixée à 50.

Lorsque nous demandons la valeur de "foo", nous nous attendons à obtenir 25 en conséquence. Les appels suivants seront effectués dans l'ordre :

>extruder_stack.getProperty("foo", "value")
>user.getProperty("foo", "value") -> Returns None
>quality_changes.getProperty("foo", "value") -> Returns None
>intent.getProperty("foo", "value") -> Returns None
>quality.getProperty("foo", "value") -> Returns "=bar/2"
>user.getProperty("bar", "value") -> returns None
>quality_changes.getProperty("bar", "value) -> Returns None
>intent.getProperty("bar", "value) -> Returns None
>quality.getProperty("bar", "value) -> Returns None
>material.getProperty("bar", "value) -> Returns 50

## Profiles

Les profils ont une certaine interdépendance les uns avec les autres, comme on peut le voir sur la photo ci-dessous. 

![Profile Structure](Profile-Structure.png)

### Utilisateur

Les paramètres de l'utilisateur sont tous les changements qui ne sont pas enregistrés dans un profil. Dans l'interface, une icône circulaire de réinitialisation est affichée pour chacun de ces paramètres. Ils sont totalement indépendants de la qualité, des changements de qualité ou de l'intention. Ils sont uniquement "liés" à une machine.

### Changements de qualité

Les modifications de qualité contiennent les paramètres que l'utilisateur a modifiés et enregistrés dans un profil. Ainsi, un profil unique généré par un utilisateur contient au moins 2 fichiers (un quality_change pour l'extrudeuse et un pour la pile globale). Les modifications de qualité sont uniquement liées au type_qualité, puisqu'elles décrivent un "delta" à appliquer sur une qualité. Ainsi, même si une qualité change parce qu'un matériau change, le profil des modifications de qualité peut rester le même (puisqu'il n'y a qu'un lien, le quality_type reste le même)

### Objectif

Les profils d'intention contiennent des paramètres qui modifient la qualité en leur donnant une intention (par exemple : "Engineering" ou "Smooth"). Ces profils dépendent de l'article, de la variante et du type_qualité

### Qualité

Les profils de qualité conservent la résolution de l'impression en réglant la hauteur des couches. Comme toutes les extrudeuses doivent avoir la même hauteur de couche, cette valeur est fixée dans la partie global_stack de la qualité.

### Matière

Conservez tous les paramètres définis par la matière active.

### Variante

La variante, dans le cas de l'extrudeuse, contient des réglages qui ont trait à la taille de la buse ou des réglages spécifiques qui s'y rapportent.

### Définition changes

Si un utilisateur apporte des modifications à une certaine machine, mais pas au point de la considérer comme un type de machine entièrement nouveau, les réglages sont enregistrés ici.

### Définition

Les paramètres par défaut de la machine.