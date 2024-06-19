<?xml version="1.0" encoding="utf-8"?>

<!DOCTYPE xsl:stylesheet  [

    <!ENTITY nbsp   "&#160;">
    <!ENTITY copy   "&#169;">
    <!ENTITY reg    "&#174;">
    <!ENTITY trade  "&#8482;">
    <!ENTITY mdash  "&#8212;">
    <!ENTITY ldquo  "&#8220;">
    <!ENTITY rdquo  "&#8221;"> 
    <!ENTITY pound  "&#163;">
    <!ENTITY yen    "&#165;">
    <!ENTITY euro   "&#8364;">

]>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="html" encoding="utf-8" doctype-public="-//W3C//DTD XHTML 1.0 Transitional//EN" doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"/>
<xsl:template match="/">

<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<title>Dictionnaire de données</title>
<link rel="stylesheet" href="xsl/css/ems.css" type="text/css"/>
</head>
<body class="general">
	<div id="conteneur">
		<div id="panneau">
			<span class="bandeau_milieu">
				<div class="titreappli">Dictionnaire de données</div>
			</span>
			<span id="header"></span>           
		</div>

		<div id="contenu">
			<div id="paragraphe">
				<span  class="pavedroit">
					<P id="date"><xsl:value-of select="structure/metas/@date_extraction"/></P>
				</span>
				<span  class="pavegauche">
					<h1 id="sommaire1"><xsl:value-of select="structure/@alias"/></h1>
				</span>
				

				<span  class="pavegauche">
					<h1 id="sommaire">Sommaire</h1>
				</span>

				<span  class="pavegauche">
					<h2>Tables</h2>
				</span>
					<span  class="pavegauche">
						<ul>
							<xsl:for-each select="structure/schemas/schema/classes/classe">
								<li>
										<a href="#{@groupe}_{@nom}"><xsl:value-of select="@nom"/></a>
										<i class="italique">
										<xsl:choose>
											<xsl:when test="@type='ALPHA'"> (Alphanumérique - </xsl:when>
											<xsl:when test="@type='POINT'"> (Point - </xsl:when>
											<xsl:when test="@type='LIGNE'"> (Ligne - </xsl:when>
											<xsl:when test="@type='SURFACE'"> (Polygone - </xsl:when>
										</xsl:choose>
										<xsl:value-of select='format-number(@nb_objets, "###,###")'/> objets)
											</i>
								</li>
							</xsl:for-each>
						</ul>
					</span>

				<span  class="pavegauche">
					<h2>Enumérations</h2>
				</span>
					<span  class="pavegauche">
						<ul>
							<xsl:for-each select="structure/conformites/conformite">
								<li><a href="#{@nom}"><xsl:value-of select="@nom"/></a></li>
							</xsl:for-each>
						</ul>
					</span>
			</div>

					
			
				<span  class="pavegauche">
					<h1>Tables</h1>
				</span>
								
								<xsl:for-each select="structure/schemas/schema/classes/classe">
									<span  class="pavegauche">
									<h2 id="{@groupe}_{@nom}">
										<xsl:value-of select="@nom"/>
										<xsl:choose>
											<xsl:when test="@type='ALPHA'"> (Alphanumérique)</xsl:when>
											<xsl:when test="@type='POINT'"> (Vectoriel : Point)</xsl:when>
											<xsl:when test="@type='LIGNE'"> (Vectoriel : Ligne)</xsl:when>
											<xsl:when test="@type='SURFACE'"> (Vectoriel : Polygone)</xsl:when>
										</xsl:choose>
									</h2>
									</span>

										<span  class="pavegauche">
											<p>
												<h3>Description</h3><br />
												<ul>
													<li class="texte">Alias : 
															<xsl:choose>
    															<xsl:when test="contains(@alias, '|')">
    																<xsl:value-of select='substring-before(@alias, "|")'/>
    															</xsl:when>
    															<xsl:otherwise>
    																<xsl:value-of select="@alias"/>
    															</xsl:otherwise>
    														</xsl:choose>
    												</li>
													<li class="texte">Définition :
													 		<xsl:choose>
														    	<xsl:when test="contains(@alias, '|')">
    																<xsl:value-of select='substring-after(@alias, "|")'/>
    															</xsl:when>
    															<xsl:otherwise>
    																-
    															</xsl:otherwise>
    														</xsl:choose>

													</li>
													<li class="texte">Nombre d'objets : <xsl:value-of select='format-number(@nb_objets, "###,###")'/></li>
													<li class="texte">Schéma : <xsl:value-of select="@groupe"/></li>
												</ul>
											</p>
										</span>
										<span  class="pavegauche">
											<h3>Attributs</h3>
										</span>

									<span  class="pavegauche">
									<table width="1000" border="1" cellspacing="0" cellpadding="0">
									  <tr>
									  	<th scope="col"></th>
									    <th scope="col">Nom attribut</th>
									    <th scope="col">Type</th>
									    <th scope="col">Type postgres</th>
									    <th scope="col">Alias</th>
									    <th scope="col">Définition</th>
									  </tr>

									  <xsl:for-each select="attribut">
										  <tr>
										    <td>
										    	<xsl:if test="@clef_primaire = 'oui'"><img src="xsl/images/cle_primaire.svg" width="16px"/></xsl:if>
										    	<xsl:if test="@clef_etrangere != ''">#</xsl:if>
										    </td>
										    <td>
										    	<xsl:value-of select="@nom"/>&nbsp;
										    	<xsl:if test="@clef_etrangere != ''">
										    		<a href="#{@cible_schema}_{@cible_classe}"><xsl:value-of select="@cible_schema"/>.<xsl:value-of select="@cible_classe"/>.<xsl:value-of select="@cible_attribut"/></a>
										    	</xsl:if>
										    </td>
										    <td><xsl:value-of select="@type"/></td>
										    <td>
										    	<xsl:choose>
										    		<xsl:when test="@type='enum'"><a href="#{@type_base}"><xsl:value-of select="@type_base"/></a></xsl:when>
										    		<xsl:otherwise><xsl:value-of select="@type_base"/></xsl:otherwise>
										    	</xsl:choose>
										    </td>
										    <td>
										    	<xsl:choose>
													<xsl:when test="contains(@alias, '|')">
    													<xsl:value-of select='substring-before(@alias, "|")'/>
    												</xsl:when>
    												<xsl:otherwise>
    													<xsl:value-of select="@alias"/>
    												</xsl:otherwise>
    											</xsl:choose>
										    </td>
										    <td>
										    	<xsl:choose>
													<xsl:when test="contains(@alias, '|')">
    													<xsl:value-of select='substring-after(@alias, "|")'/>
    												</xsl:when>
    												<xsl:otherwise>
    													-
    												</xsl:otherwise>
    											</xsl:choose>
    										</td>
										  </tr>
									  </xsl:for-each>
									  </table>
									</span>
									<span  class="pavedroit">
									  <a href="#null" onclick="javascript:history.back();">Retour</a> - <a href="#sommaire">Sommaire</a>
									</span>
								</xsl:for-each>
							
					
			
			
				<span  class="pavegauche">
					<h1>Enumérations</h1>
				</span>
							
									<xsl:for-each select="structure/conformites/conformite">
										<span  class="pavegauche">
											<h2 id="{@nom}"><xsl:value-of select="@nom"/></h2>
										</span>
										<span  class="pavegauche">
											<table width="1000" border="1" cellspacing="0" cellpadding="0">
											  <tr>
											  	<th scope="col">Valeur</th>
											    <th scope="col">Alias</th>
											  </tr>
											  <xsl:for-each select="VALEUR">
												  <tr>
												    <td><xsl:value-of select="@v"/></td>
												    <td><xsl:value-of select="@alias"/></td>
												  </tr>
											  </xsl:for-each>
											  </table>
										</span>
										<span  class="pavedroit">
									  		<a href="#null" onclick="javascript:history.back();">Retour</a> - <a href="#sommaire">Sommaire</a>
										</span>
									</xsl:for-each>
				
					
								
		
		</div>
	</div>



</body>
</html>

</xsl:template>
</xsl:stylesheet>