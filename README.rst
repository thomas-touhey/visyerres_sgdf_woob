Vis'Yerres SGDF - Modules Woob
==============================

Vous avez le sentiment que l'intranet des Scouts et Guides de France ne
convient pas à l'usage de votre groupe ?
Vous réalisez une application s'orientant à l'usage unique de ce
groupe, et souhaitez interagir avec l'intranet ?
Vous avez toqué à la bonne porte !

Ce projet définit des modules Woob_ pour interagir avec l'intranet SGDF,
ainsi qu'avec quelques autres ressources.

Un exemple d'utilisation est le suivant :

.. code-block:: python

    from visyerres_sgdf_woob import MODULES_PATH
    from woob.core.ouiboube import WebNip

    woob = WebNip(modules_path=MODULES_PATH)
    backend = woob.build_backend('intranetsgdf', params={
        'code': '16XXXXXXX',
        'password': '#VOTRE MOT DE PASSE ICI#',
    })

    person = backend.get_current_person()

    print('First name:', person.first_name)
    print('Last name:', person.last_name)
    print('Civility title:', person.title)

.. _Woob: https://woob.tech/
