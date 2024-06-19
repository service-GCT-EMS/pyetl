# -*- coding: utf-8 -*-
"""
Acces aux bases de donnees postgis

commandes disponibles :

    * lecture des structures et de droits
    * lecture des fonctions et des triggers et tables distantes gestion des clefs etrangeres
    * extraction multitables et par selection sur un attribut et par geometrie
    * ecriture de structures en fichier sql
    * ecritures de donnees au format copy et chargment en base par psql
    * passage de requetes sql
    * insert et updates en base '(beta)'

necessite la librairie psycopg2 et l acces au loader psql pour le chargement de donnees

il est necessaire de positionner les parametres suivant:


"""
from .base_postgres import PgrConnect
from .postgres_gensql import PgrGenSql


RESERVES = {"analyse": "analyse_pb", "type": "type_entite", "as": "ass"}

GTYPES_DISC = {
    "alpha": "",
    "ALPHA": "",
    "ponctuel": "geometry(point,3948)",
    "POINT": "geometry(point,3948)",
    "POINT MULTIPLE": "geometry(point,3948)",
    "POINT MULTIPLE 3D": "geometry(pointz,3948)",
    "POINT 3D": "geometry(pointz,3948)",
    "LIGNE": "geometry(linestring,3948)",
    "lineaire": "geometry(linestring,3948)",
    "lineaire MULTIPLE": "geometry(linestring,3948)",
    "LIGNE MULTIPLE": "geometry(multilinestring,3948)",
    "LIGNE 3D": "geometry(linestringZ,3948)",
    "LIGNE MULTIPLE 3D": "geometry(multilinestringZ,3948)",
    "POLYGONE": "geometry(polygon,3948)",
    "surfacique": "geometry(polygon,3948)",
    "surfacique MULTIPLE": "geometry(polygon,3948)",
    "POLYGONE 3D": "geometry(polygonZ,3948)",
    "POLYGONE MULTIPLE": "geometry(multipolygon,3948)",
    "POLYGONE MULTIPLE 3D": "geometry(multipolygonZ,3948)",
    "GEOMETRIE": "geometry",
    "GEOMETRIE MULTIPLE": "geometry",
    "GEOMETRIE MULTIPLE 3D": "geometry",
    "GEOMETRIE 3D": "geometry",
}
GTYPES_CURVE = {
    "alpha": "",
    "ALPHA": "",
    "ponctuel": "geometry(point,3948)",
    "POINT": "geometry(point,3948)",
    "POINT MULTIPLE": "geometry(point,3948)",
    "POINT MULTIPLE 3D": "geometry(point,3948)",
    "POINT 3D": "geometry(pointz,3948)",
    "LIGNE": "geometry(linestring,3948)",
    "lineaire": "geometry(linestring,3948)",
    "lineaire MULTIPLE": "geometry(linestring,3948)",
    "LIGNE MULTIPLE": "geometry(multicurve,3948)",
    "LIGNE 3D": "geometry(linestringZ,3948)",
    "LIGNE MULTIPLE 3D": "geometry(multicurveZ,3948)",
    "POLYGONE": "geometry(polygon,3948)",
    "surfacique": "geometry(polygon,3948)",
    "surfacique MULTIPLE": "geometry(polygon,3948)",
    "POLYGONE 3D": "geometry(polygonZ,3948)",
    "POLYGONE MULTIPLE": "geometry(multisurface,3948)",
    "POLYGONE MULTIPLE 3D": "geometry(multisurfaceZ,3948)",
    "GEOMETRIE": "geometry",
    "GEOMETRIE MULTIPLE": "geometry",
    "GEOMETRIE MULTIPLE 3D": "geometry",
    "GEOMETRIE 3D": "geometry",
}


class PgsConnect(PgrConnect):
    """connecteur de la base de donnees postgres"""

    def __init__(
        self, serveur, base, user, passwd, debug=0, system=False, params=None, code=None
    ):
        super().__init__(serveur, base, user, passwd, debug, system, params, code)

        self.gtypes_curve = GTYPES_CURVE
        self.gtypes_disc = GTYPES_DISC
        self.accept_sql = "geo"
        self.geographique = True
        self.dialecte = "postgis"
        self.type_base = "postgis"
        self.defsrid = "3948"
        self.requetes["info_tables"] = self.requetes["info_tables_g"]

    @property
    def req_tables(self):
        """recupere les tables de la base"""
        print ('req table postgis')
        return self.requetes["info_tables"], None



    def get_type(self, nom_type):
        if "geometry" in nom_type:
            return nom_type
        if nom_type.upper() not in self.types_base:
            print(" type non trouve", nom_type, self.types_base)
        return self.types_base.get(nom_type.upper(), "?")

    def get_surf(self, nom):
        return "ST_area(%s)" % nom

    def get_perim(self, nom):
        return "ST_perimeter(%s)" % nom

    def get_long(self, nom):
        return "ST_length(%s)" % nom

    def get_geom(self, nom):
        return "ST_asEWKT(%s)" % nom

    # def set_geom(self, geom, srid):
    #     return "ST_GeomFromText('%s',%s)" % (geom, srid)

    def set_geom(self, geom, srid):
        if not srid:
            srid = self.defsrid
        return "ST_SetSrid(ST_MakeValid('%s'::geometry),%s)" % (geom, srid)

    # def set_geomb(self, geom, srid, buffer):
    #     return "ST_buffer(ST_GeomFromText('%s',%s),%f))" % (geom, srid, buffer)

    def set_geomb(self, geom, srid, buffer):
        return "ST_buffer(%s,%f)" % (self.set_geom(geom, srid), buffer)

    def set_limit(self, maxi, _):
        if maxi:
            return " LIMIT " + str(maxi)
        return ""

    def cond_geom(self, nom_fonction, nom_geometrie, geom2):
        cond = ""
        fonction = ""
        if not geom2:
            self.params.logger.error("pas de geometrie")
            raise StopIteration(1)
        if nom_fonction == "dans_emprise":
            cond = geom2 + " && " + nom_geometrie
        else:
            if nom_fonction == "intersect":
                fonction = "ST_Intersects("
            elif nom_fonction == "dans":
                fonction = "ST_Contains("
            if fonction:
                cond = fonction + geom2 + "," + nom_geometrie + ")"
        if not cond:
            self.params.logger.error("pas de condition geometrique %s ", nom_fonction)
            raise StopIteration(1)
        # print("cond geom", nom_fonction, fonction, geom2)
        return cond


class PgsGenSql(PgrGenSql):
    """classe de generation des structures sql"""

    def __init__(self, connection=None, basic=False):
        super().__init__(connection=connection, basic=basic)
        self.geom = True
        self.courbes = False
        self.schemas = True
        self.reserves = RESERVES  # mots reserves et leur remplacement
        self.typenum = {
            "1": "POINT",
            "2": "LIGNE",
            "3": "POLYGONE",
            "-1": "GEOMETRIE",
            "0": "ALPHA",
            "indef": "ALPHA",
        }
        self.gtypes_disc = GTYPES_DISC
        self.gtypes_curve = GTYPES_CURVE
        self.type_courbes = "disc"
        self.dialecte = "postgis"

    def cree_indexes(self, schemaclasse, groupe, nom):
        """creation des indexes"""
        ctr, idx = super().cree_indexes(schemaclasse, groupe, nom)
        geomt, arc = self.get_type_geom(schemaclasse)
        if geomt != "0":
            idx.append(
                "CREATE INDEX "
                + nom
                + "_gist ON "
                + groupe
                + "."
                + nom
                + " USING gist(geometrie);"
            )
        return ctr, idx

    def getgeomsql(self, classe):
        """retourne la definition sql de la geometrie"""
        geomt, arc = self.get_type_geom(classe)
        # print ('getgeomsql: type_geom',classe.identclasse, classe.info["type_geom"], geomt)
        if geomt and geomt.upper() != "ALPHA" and geomt != "0":
            if self.type_courbes == "curve" and arc:
                return "\tgeometrie public." + self.gtypes_curve[geomt] + ","
            else:
                return "\tgeometrie public." + self.gtypes_disc[geomt] + ","
        return ""

    def prepare_style(self, ident, conf):
        """# prepare un style par defaut pour la table"""
        schema = self.schema
        classe = schema.classes[ident]
        # print "traitement classe ", groupe,nom
        _, nom = self.get_nom_base(ident)
        atts = classe.get_liste_attributs()
        nom_style = nom
        if len(nom_style) > 28:
            nom_style = nom_style[:28]
        nom_style = nom_style + "_d"
        als = ["<aliases>"]
        index = 0
        style = [
            "<!DOCTYPE qgis PUBLIC ''http://mrcc.com/qgis.dtd'' ''SYSTEM''>",
            """<qgis version="2.8.1-Wien" minimumScale="0" maximumScale="1e+08"
                 simplifyDrawingHints="1" minLabelScale="0" maxLabelScale="1e+08"
                 simplifyDrawingTol="1" simplifyMaxScale="1" hasScaleBasedVisibilityFlag="0"
                 simplifyLocal="1" scaleBasedLabelVisibilityFlag="0">""",
            "<edittypes>",
        ]

        for nom_att in atts:
            accessoires = ""
            attribut = classe.attributs[nom_att]
            editable = "1"
            editype = "TextEdit"
            # print (a,attribut.type_att,attribut.conformite)
            complements = ""
            if attribut.defaut in ("A", "S", "I"):
                editable = "0"
            if attribut.conformite:
                if conf:
                    editype = "Enumeration"
                else:
                    editype = "ValueMap"
                    accessoires = "\n".join(
                        [
                            '<value key="' + i + '" value="' + i + '"/>'
                            for i in sorted(
                                list(attribut.conformite.stock.values()),
                                key=lambda v: v[2],
                            )
                        ]
                    )
            elif attribut.type_att in self.types_base:
                typb = self.types_base[attribut.type_att]
                #                print ('typage attributs', nom_att, attribut.type_att, typb)
                if typb in {"timestamp", "D", "DS", "TIMESTAMP", "d", "ds"}:
                    editype = "DateTime"
                    complements = (
                        'calendar_popup="1" allow_null="1" '
                        + 'display_format="dd/MM/yyyy" field_format="dd/MM/yyyy"'
                    )
                    if editable == "0":
                        # complements='calendar_popup="0" allow_null="1" display_format="dd/MM/yyyy" '
                        editype = "TextEdit"
                        complements = ' IsMultiline="0" UseHtml="0"'

                elif typb == "boolean" or typb == "B":
                    editype = "CheckBox"
                    complements = (
                        'UncheckedState="f" constraint="" CheckedState="t" '
                        + 'labelOnTop="0" constraintDescription="" notNull="0"/>'
                    )

                else:
                    editype = "TextEdit"
                    complements = ' IsMultiline="0" UseHtml="0"'

            edit = (
                '<edittype widgetv2type="'
                + editype
                + '" '
                + ' name="'
                + nom_att.lower()
                + '">\n'
                + '<widgetv2config fieldEditable="'
                + editable
                + '" '
                + complements
                + ' labelOnTop="0"/>\n'
                + accessoires
                + "</edittype>"
            )
            style.append(edit)
        style.append("</edittypes>")
        style.append("<editorlayout>generatedlayout</editorlayout>")
        for nom_att in atts:
            attribut = classe.attributs[nom_att]
            if attribut.alias:
                adef = (
                    '<alias field="'
                    + nom_att.lower()
                    + '" index="'
                    + str(index)
                    + '" name="'
                    + attribut.alias.replace("'", "''")
                    + '"/>'
                )
                als.append(adef)
                index += 1
        style.extend(als)
        style.append("</aliases>")
        style.append("</qgis>")
        return nom_style, "\n".join(style)

    def db_cree_table(self, schema, ident):
        """creation d' une tables en direct"""
        req = self.cree_tables(schema, ident)
        if self.connection:
            return self.connection.request(req, ())

    def db_cree_tables(self, schema, liste):
        """creation d'une liste de tables en direct"""
        if not liste:
            liste = [i for i in self.schema.classes if self.schema.classes[i].a_sortir]
        for ident in liste:
            self.db_cree_table(schema, ident)

    def dbloadfile(self, schema, ident, fichier):
        """# charge un fichier par copy"""
        cur = self.connection.cursor()
        colonnes = tuple(schema.classes[ident].get_liste_attributs())
        nom = ".".join(ident)
        with open(fichier) as infile:
            try:
                cur.copy_from(infile, nom, columns=colonnes, sep="\t")
                cur.close()
                return True
            except Exception as erreur:
                self.params.logger.exception(
                    "erreur chargement %s", fichier, exc_info=erreur
                )
                # print("error: sigli: chargement ", fichier, "-->", erreur)
                cur.close()
                return False

    def dbload(self, schemaclasse, ident, source):
        """charge des objets en base de donnees par dbload"""
        cur = self.connection.cursor()
        colonnes = tuple(schemaclasse.get_liste_attributs())
        nom = ".".join(ident)
        try:
            cur.copy_from(source, nom, columns=colonnes, sep="\t")
            cur.close()
            return True
        except Exception as erreur:
            self.params.logger.exception("erreur chargement %s", ident, exc_info=erreur)
            # print("error: sigli: chargement ", ident, "-->", erreur)
            cur.close()
            return False

    # ==== initialiseurs pour la gestion de la geometrie ====
    @staticmethod
    def _commande_geom_strict(niveau, classe, strict, gtyp="0", dim="2", courbe=False):
        """manipulation de la geometrie pour la discretisation des courbes"""
        #        print ('geom strict ',niveau, classe, strict, gtyp)
        cmpz = "Z" if dim == "3" else ""
        if not strict:
            return (
                "ALTER TABLE "
                + niveau.lower()
                + "."
                + classe.lower()
                + " ALTER COLUMN geometrie TYPE Geometry(Geometry"
                + cmpz
                + ",3948);\n"
            )
        else:
            if courbe:
                geom = "MultiCurve" if gtyp == "2" else "MultiSurface"
                fonction = " SET geometrie = ST_ForceCurve(geometrie); \n"
            else:
                geom = "MultiLinestring" if gtyp == "2" else "Multipolygon"
                fonction = " SET geometrie = ST_CurveToLine(geometrie); \n"
            return (
                "UPDATE "
                + niveau.lower()
                + "."
                + classe.lower()
                + fonction
                + "ALTER TABLE "
                + niveau.lower()
                + "."
                + classe.lower()
                + " ALTER COLUMN geometrie TYPE Geometry("
                + geom
                + cmpz
                + ",3948);\n"
            )

    # @staticmethod
    # def _commande_geom_courbe(niveau, classe, gtyp="0", dim="2", courbe=False):
    #     """manipulation de la geometrie pour la conservation des courbes"""
    #     cmpz = "Z" if dim == "3" else ""
    #     if courbe:
    #         geom = "MultiCurve" if gtyp == "2" else "MultiSurface"
    #     else:
    #         geom = "MultiLinestring" if gtyp == "2" else "Multipolygon"
    #     return (
    #         "UPDATE "
    #         + niveau.lower()
    #         + "."
    #         + classe.lower()
    #         + " SET geometrie = ST_ForceCurve(geometrie); \n"
    #         + "ALTER TABLE "
    #         + niveau.lower()
    #         + "."
    #         + classe.lower()
    #         + " ALTER COLUMN geometrie TYPE Geometry("
    #         + geom
    #         + cmpz
    #         + ",3948);\n"
    #     )

    @staticmethod
    def _commande_index_gist(niveau, classe, drop):
        """suppression des index geometriques pour accelerer le chargement"""
        if drop:
            return "DROP INDEX " + niveau.lower() + "." + classe.lower() + "_gist;\n"
        else:
            return (
                "CREATE INDEX "
                + classe.lower()
                + "_gist ON "
                + niveau.lower()
                + "."
                + classe.lower()
                + " USING gist(geometrie);\n"
            )

    # structures specifiques pour stocker les scrips en base
    # cree 4 tables: Macros scripts batchs logs

    def init_pyetl_script(self, nom_schema):
        """cree les structures standard"""
        pass


DBDEF = {
    "postgis": (
        PgsConnect,
        PgsGenSql,
        "server",
        "",
        "#ewkt",
        "base postgres avec postgis générique",
    )
}
