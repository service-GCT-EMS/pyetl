SELECT pg_views.schemaname AS nomschema,
	pg_views.viewname AS nomtable,
	pg_views.definition,
	false AS materialise
   FROM pg_views
  WHERE pg_views.schemaname != 'pg_catalog' AND pg_views.schemaname != 'information_schema'
UNION
 SELECT pg_matviews.schemaname AS nomschema,
	pg_matviews.matviewname AS nomtable,
	pg_matviews.definition,
	true AS materialise
   FROM pg_matviews;