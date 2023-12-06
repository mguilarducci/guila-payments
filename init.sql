--
-- PostgreSQL database dump
--

-- Dumped from database version 15.4 (Debian 15.4-2.pgdg120+1)
-- Dumped by pg_dump version 15.4 (Debian 15.4-2.pgdg120+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: pix_keys; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pix_keys (
    id integer NOT NULL,
    key_name character varying(100),
    owner character varying(100)
);


ALTER TABLE public.pix_keys OWNER TO postgres;

--
-- Name: pix_keys_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pix_keys_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pix_keys_id_seq OWNER TO postgres;

--
-- Name: pix_keys_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.pix_keys_id_seq OWNED BY public.pix_keys.id;


--
-- Name: pix_keys id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pix_keys ALTER COLUMN id SET DEFAULT nextval('public.pix_keys_id_seq'::regclass);


--
-- Data for Name: pix_keys; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pix_keys (id, key_name, owner) FROM stdin;
\.


--
-- Name: pix_keys_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.pix_keys_id_seq', 1, false);


--
-- Name: pix_keys pix_keys_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pix_keys
    ADD CONSTRAINT pix_keys_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

