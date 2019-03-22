# -*- coding: utf-8 -*-
"""
Created on Tue Apr 17 23:30:25 2018

@author: claude
"""


def xml_script_metadata(mapper):
    """ cree les entetes de colonnes """
    colonnes = mapper.noms_champs_n
    xml = ["<metadata>"]
    for i in colonnes:
        xml.append(
            '<column editable="true" datatype="string" label="'
            + i
            + '" name="country'
            + i
            + '">'
        )
        if i == "commande":
            xml.append(
                '<column editable="true" datatype="string" label="'
                + i
                + '" name="country'
                + i
                + '"/>'
            )
            xml.append("<values>")
            for j in mapper.commandes:
                xml.append('<value value="' + j + '">' + j + "</value>")
            xml.append("</values>")
        xml.append("</column>")
    xml.append("</metadata>")


def crexml_from_script(mapper, script):
    """convertit un script en xml editable """
    xml = '<?xml version="1.0" encoding="UTF-8"?>'
    metadata = xml_script_metadata(mapper)


"""
<?xml version="1.0" encoding="UTF-8"?>
-<table>
<metadata>
    <column editable="true" datatype="string" label="NAME" name="name"/>
    <column editable="true" datatype="string" label="FIRSTNAME" name="firstname"/>
    <column editable="true" datatype="integer" label="AGE" name="age"/>
    <column editable="true" datatype="double(m,2)" label="HEIGHT" name="height"/>
    <column editable="true" datatype="string" label="COUNTRY" name="country">
        <values>
        <group label="Europe">
            <value value="be">Belgium</value>
            <value value="fr">France</value>
            <value value="uk">Great-Britain</value>
            <value value="nl">Nederland</value>
        </group>
        
        -group label="America">
            <value value="br">Brazil</value>
            <value value="ca">Canada</value>
            <value value="us">USA</value>
        </group>
        <group label="Africa">
            <value value="ng">Nigeria</value>
            <value value="za">South-Africa</value>
            <value value="zw">Zimbabwe</value>
        </group>
        </values>
        </column>
    <column editable="true" datatype="email" label="EMAIL" name="email"/>
    <column editable="true" datatype="boolean" label="FREELANCE" name="freelance"/>
    <column editable="true" datatype="date" label="LAST VISIT" name="lastvisit"/>
</metadata>
<data>
<!-- NB: It is recommended to name your columns. This way you can give them in any order and skip some columns if you want. -->


    <row id="1">
        <column name="country">uk</column>
        <column name="age">33</column>
        <column name="name">Duke</column>
        <column name="firstname">Patience</column>
        <column name="height">1.842</column>
        <column name="email">patience.duke@gmail.com</column>
        <column name="lastvisit">11/12/2002</column>
    </row>

</data>
</table>
"""
