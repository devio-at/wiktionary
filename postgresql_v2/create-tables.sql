
CREATE DATABASE wiktionary WITH ENCODING 'UTF8';

CREATE TABLE public.wikisite (
	id serial4 NOT NULL,
	language_id varchar(10) NOT NULL,
	filename varchar(200) NOT NULL,
	sitename varchar(50) NOT NULL,
	dbname varchar(50) NOT NULL,
	base varchar(200) NOT NULL,
	case_sensitive bool NOT NULL,
	created timestamp NOT NULL DEFAULT now(),
	CONSTRAINT wikisite_pk PRIMARY KEY (id)
);

CREATE TABLE public.wikinamespace (
	id serial4 NOT NULL,
	site_id int4 NOT NULL,
	"key" int4 NOT NULL,
	case_sensitive bool NOT NULL,
	"name" varchar(100) NULL,
	CONSTRAINT wikinamespace_pk PRIMARY KEY (id),
	CONSTRAINT wikinamespace_un UNIQUE (site_id, key)
);

ALTER TABLE public.wikinamespace ADD CONSTRAINT wikinamespace_fk FOREIGN KEY (site_id) REFERENCES public.wikisite(id) ON DELETE CASCADE;

CREATE TABLE public.page (
	id serial4 NOT NULL,
	site_id int4 NOT NULL,
	page_id int8 NOT NULL,
	namespace_key int4 NOT NULL,
	language_id varchar(10) NOT NULL,
	title varchar(400) NOT NULL,
	"timestamp" timestamp NULL,
	page_text text NOT NULL,
	created timestamp NOT NULL DEFAULT now(),
	CONSTRAINT page_pk PRIMARY KEY (id)
);
CREATE UNIQUE INDEX page_site_id_idx ON public.page USING btree (site_id, page_id);

ALTER TABLE public.page ADD CONSTRAINT page_fk FOREIGN KEY (site_id) REFERENCES public.wikisite(id) ON DELETE CASCADE;
ALTER TABLE public.page ADD CONSTRAINT page_fk_1 FOREIGN KEY (site_id,namespace_key) REFERENCES public.wikinamespace(site_id,"key");
