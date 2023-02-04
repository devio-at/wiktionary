CREATE TABLE public.page (
	id serial4 NOT NULL,
	"source" varchar(200) NOT NULL,
	language_id varchar(10) NOT NULL,
	page_id int8 NOT NULL,
	title varchar(400) NOT NULL,
	"timestamp" timestamp NULL,
	page_text text NOT NULL,
	created timestamp NOT NULL DEFAULT now(),
	CONSTRAINT page_pk PRIMARY KEY (id)
);
CREATE UNIQUE INDEX page_source_idx ON public.page USING btree (source, page_id);
