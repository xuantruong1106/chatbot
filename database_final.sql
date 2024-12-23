PGDMP  /    4            
    |            chatbot    16.4    16.4 .               0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false                       0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false                       0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false                       1262    33363    chatbot    DATABASE     �   CREATE DATABASE chatbot WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'English_United States.utf8';
    DROP DATABASE chatbot;
                postgres    false            �            1255    33421 %   get_answer_id_faq_from_key_word(text)    FUNCTION     a  CREATE FUNCTION public.get_answer_id_faq_from_key_word(keyword text) RETURNS TABLE(kw_answer_text text)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT answer
    FROM faq
    WHERE id = (
        SELECT id_faq
        FROM suggestion
        WHERE key_word = keyword
        ORDER BY id_faq
        LIMIT 1
    )
    LIMIT 1;
END;
$$;
 D   DROP FUNCTION public.get_answer_id_faq_from_key_word(keyword text);
       public          postgres    false            �            1255    33422    get_faq_answer(text)    FUNCTION     �   CREATE FUNCTION public.get_faq_answer(question_client text) RETURNS TABLE(answer_get text)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT answer
    FROM faq
    WHERE faq.question = question_client;
END;
$$;
 ;   DROP FUNCTION public.get_faq_answer(question_client text);
       public          postgres    false            �            1255    33423    get_id_faq(text)    FUNCTION       CREATE FUNCTION public.get_id_faq(des text) RETURNS TABLE(answer_text text)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT answer
    FROM faq
    WHERE id = (
        SELECT id_faq
        FROM suggestion
        WHERE description = des
    );
END;
$$;
 +   DROP FUNCTION public.get_id_faq(des text);
       public          postgres    false            �            1255    33425     insert_faq_procedure(text, text) 	   PROCEDURE     �   CREATE PROCEDURE public.insert_faq_procedure(IN question text, IN answer text)
    LANGUAGE plpgsql
    AS $$
BEGIN
    INSERT INTO faq (question, answer) 
    VALUES (question, answer);
END;
$$;
 N   DROP PROCEDURE public.insert_faq_procedure(IN question text, IN answer text);
       public          postgres    false            �            1255    33424    suggestion(text)    FUNCTION     �   CREATE FUNCTION public.suggestion(string_input text) RETURNS TABLE(ques text)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN query
    SELECT description
    FROM suggestion
    WHERE key_word ILIKE '%' || string_input || '%';
END;

$$;
 4   DROP FUNCTION public.suggestion(string_input text);
       public          postgres    false            �            1259    33364    faq    TABLE     k   CREATE TABLE public.faq (
    id integer NOT NULL,
    question text NOT NULL,
    answer text NOT NULL
);
    DROP TABLE public.faq;
       public         heap    postgres    false            �            1259    33369 
   faq_id_seq    SEQUENCE     �   CREATE SEQUENCE public.faq_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 !   DROP SEQUENCE public.faq_id_seq;
       public          postgres    false    215                       0    0 
   faq_id_seq    SEQUENCE OWNED BY     9   ALTER SEQUENCE public.faq_id_seq OWNED BY public.faq.id;
          public          postgres    false    216            �            1259    33370    logs    TABLE       CREATE TABLE public.logs (
    id integer NOT NULL,
    username character varying(255) NOT NULL,
    question text NOT NULL,
    answer text,
    is_answered boolean DEFAULT false NOT NULL,
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);
    DROP TABLE public.logs;
       public         heap    postgres    false            �            1259    33377    logs_id_seq    SEQUENCE     �   CREATE SEQUENCE public.logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 "   DROP SEQUENCE public.logs_id_seq;
       public          postgres    false    217                       0    0    logs_id_seq    SEQUENCE OWNED BY     ;   ALTER SEQUENCE public.logs_id_seq OWNED BY public.logs.id;
          public          postgres    false    218            �            1259    33407 
   suggestion    TABLE     y   CREATE TABLE public.suggestion (
    id integer NOT NULL,
    key_word text,
    description text,
    id_faq integer
);
    DROP TABLE public.suggestion;
       public         heap    postgres    false            �            1259    33406    suggestion_id_seq    SEQUENCE     �   CREATE SEQUENCE public.suggestion_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 (   DROP SEQUENCE public.suggestion_id_seq;
       public          postgres    false    224                       0    0    suggestion_id_seq    SEQUENCE OWNED BY     G   ALTER SEQUENCE public.suggestion_id_seq OWNED BY public.suggestion.id;
          public          postgres    false    223            �            1259    33397    unanswered_questions    TABLE     �   CREATE TABLE public.unanswered_questions (
    id integer NOT NULL,
    question text NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);
 (   DROP TABLE public.unanswered_questions;
       public         heap    postgres    false            �            1259    33396    unanswered_questions_id_seq    SEQUENCE     �   CREATE SEQUENCE public.unanswered_questions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 2   DROP SEQUENCE public.unanswered_questions_id_seq;
       public          postgres    false    222                        0    0    unanswered_questions_id_seq    SEQUENCE OWNED BY     [   ALTER SEQUENCE public.unanswered_questions_id_seq OWNED BY public.unanswered_questions.id;
          public          postgres    false    221            �            1259    33378    users    TABLE     �   CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(50) NOT NULL,
    password text NOT NULL,
    role character varying(10) NOT NULL
);
    DROP TABLE public.users;
       public         heap    postgres    false            �            1259    33383    users_id_seq    SEQUENCE     �   CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 #   DROP SEQUENCE public.users_id_seq;
       public          postgres    false    219            !           0    0    users_id_seq    SEQUENCE OWNED BY     =   ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;
          public          postgres    false    220            i           2604    33384    faq id    DEFAULT     `   ALTER TABLE ONLY public.faq ALTER COLUMN id SET DEFAULT nextval('public.faq_id_seq'::regclass);
 5   ALTER TABLE public.faq ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    216    215            j           2604    33385    logs id    DEFAULT     b   ALTER TABLE ONLY public.logs ALTER COLUMN id SET DEFAULT nextval('public.logs_id_seq'::regclass);
 6   ALTER TABLE public.logs ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    218    217            p           2604    33410    suggestion id    DEFAULT     n   ALTER TABLE ONLY public.suggestion ALTER COLUMN id SET DEFAULT nextval('public.suggestion_id_seq'::regclass);
 <   ALTER TABLE public.suggestion ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    223    224    224            n           2604    33400    unanswered_questions id    DEFAULT     �   ALTER TABLE ONLY public.unanswered_questions ALTER COLUMN id SET DEFAULT nextval('public.unanswered_questions_id_seq'::regclass);
 F   ALTER TABLE public.unanswered_questions ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    222    221    222            m           2604    33386    users id    DEFAULT     d   ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);
 7   ALTER TABLE public.users ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    220    219                      0    33364    faq 
   TABLE DATA           3   COPY public.faq (id, question, answer) FROM stdin;
    public          postgres    false    215   L4                 0    33370    logs 
   TABLE DATA           X   COPY public.logs (id, username, question, answer, is_answered, "timestamp") FROM stdin;
    public          postgres    false    217   9                 0    33407 
   suggestion 
   TABLE DATA           G   COPY public.suggestion (id, key_word, description, id_faq) FROM stdin;
    public          postgres    false    224   �:                 0    33397    unanswered_questions 
   TABLE DATA           H   COPY public.unanswered_questions (id, question, created_at) FROM stdin;
    public          postgres    false    222   <;                 0    33378    users 
   TABLE DATA           =   COPY public.users (id, username, password, role) FROM stdin;
    public          postgres    false    219   Y;       "           0    0 
   faq_id_seq    SEQUENCE SET     9   SELECT pg_catalog.setval('public.faq_id_seq', 49, true);
          public          postgres    false    216            #           0    0    logs_id_seq    SEQUENCE SET     :   SELECT pg_catalog.setval('public.logs_id_seq', 10, true);
          public          postgres    false    218            $           0    0    suggestion_id_seq    SEQUENCE SET     ?   SELECT pg_catalog.setval('public.suggestion_id_seq', 4, true);
          public          postgres    false    223            %           0    0    unanswered_questions_id_seq    SEQUENCE SET     J   SELECT pg_catalog.setval('public.unanswered_questions_id_seq', 1, false);
          public          postgres    false    221            &           0    0    users_id_seq    SEQUENCE SET     :   SELECT pg_catalog.setval('public.users_id_seq', 2, true);
          public          postgres    false    220            r           2606    33388    faq faq_pkey 
   CONSTRAINT     J   ALTER TABLE ONLY public.faq
    ADD CONSTRAINT faq_pkey PRIMARY KEY (id);
 6   ALTER TABLE ONLY public.faq DROP CONSTRAINT faq_pkey;
       public            postgres    false    215            t           2606    33390    logs logs_pkey 
   CONSTRAINT     L   ALTER TABLE ONLY public.logs
    ADD CONSTRAINT logs_pkey PRIMARY KEY (id);
 8   ALTER TABLE ONLY public.logs DROP CONSTRAINT logs_pkey;
       public            postgres    false    217            |           2606    33414    suggestion suggestion_pkey 
   CONSTRAINT     X   ALTER TABLE ONLY public.suggestion
    ADD CONSTRAINT suggestion_pkey PRIMARY KEY (id);
 D   ALTER TABLE ONLY public.suggestion DROP CONSTRAINT suggestion_pkey;
       public            postgres    false    224            z           2606    33405 .   unanswered_questions unanswered_questions_pkey 
   CONSTRAINT     l   ALTER TABLE ONLY public.unanswered_questions
    ADD CONSTRAINT unanswered_questions_pkey PRIMARY KEY (id);
 X   ALTER TABLE ONLY public.unanswered_questions DROP CONSTRAINT unanswered_questions_pkey;
       public            postgres    false    222            v           2606    33392    users users_pkey 
   CONSTRAINT     N   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);
 :   ALTER TABLE ONLY public.users DROP CONSTRAINT users_pkey;
       public            postgres    false    219            x           2606    33394    users users_username_key 
   CONSTRAINT     W   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);
 B   ALTER TABLE ONLY public.users DROP CONSTRAINT users_username_key;
       public            postgres    false    219            }           2606    33415    suggestion fk_id_faq    FK CONSTRAINT     p   ALTER TABLE ONLY public.suggestion
    ADD CONSTRAINT fk_id_faq FOREIGN KEY (id_faq) REFERENCES public.faq(id);
 >   ALTER TABLE ONLY public.suggestion DROP CONSTRAINT fk_id_faq;
       public          postgres    false    4722    224    215               �  x��YMo�F=��b}K��$�� ��A�SӢ�\$:�����4�c�C�CQ�=�bn�1� EH=������]Q�$R�d��F����7�7�oȪ����0 Q6 ȃ�����DZ�`䱏�'p�'D�8�>���쪁l��06@�7u�)j68�ٻ��8��-]x�j���k+�d�
�j�F�4їS���p���B� vV�,�s.C,s���I�	\_� r�5�2�����X��Z��jf.
{�L]��z�.�½�"2��Whwҽ"V|񔌭�+'y�ʞ�*��P���T��%�ܙ��mf���Y��KE��8L��Pem�RR�lر��(���$.bt��l@�Λ�Ҿ7R�ٙݚeT�g.���>��ƈ�ϡ��q�N�	 ��$���vu�.I�E�%�r��N�cw�} �&Q��ԅu�wl�6Y�����i���g�k}��-x��p�6�[�W��'�j�P�}4<a�P��e�胇��(�u���!P���g������n����_}�1|�f�S�8�:�c�Z�=���a��p��k��2�_�֖n[{�d��g��j�h/R��!w%��q�(���=Iτ[__^�y]�Ne]o&�K�/7�O�p�s�<d#��Pd/�4à�^�"�������\N3�6��S3�7rpC�k���3���3d["Mq�5~駲A�<h�` �X���9��< C����:����?�h!2<�$�A�pC	���-�^���zℷ���8��B���܈��+"��ՋϽ�2�|JH~�|(0��K|���) _���4QB�oo.=�d�cj�N��	'�D&=�<�B|�4O��+aM�݆͘��S�7�c��.�}��@x���d����3J��Ϊ�z8�)2<��T����w�!]�|�RP�q3xA���RJ5�=P4�b0uC٩�e�`6/�� o�4Us!j�n\4��T�!<�}��r�bU$�hm<�R��q��]�� ���d׼�[�Mp�{�g�%��&ԊΒ)P�1HU����±G-�S��Dowc�jA:�W7�NRwI��1DT�h\�!��"�#Ə�uQ�7�tk�2��O0���^U~��zh�W՚G�5�e<ʹ{aumw�:\���B�Y�嶖]������������ �M�7� :,;?*�uF3�5�c�ԟ����<�^         �  x�픿J1���S���ƙ$����V�,,�9�,zQt|�����;���q����&�N��ϡ z�)���7�|×��0-k���eZAs=�
�D�$���8�!�J	$&'�ȂɦJsMR�& �l�v��2_���[;���
�oCa���R�=��.{��W9�� ��z�so��!�P!���	���i�i_{�.ox��˛#8v��Q��v]�B{,���h��=Do�x߇N$r�(�E�s��� ��XH����u��tl�f~���e�֌�k���VG�v����0�t�	���ߔ\h�W�>�$�/(�
qSָBZW��u-̇�x􅲜���[�O�3�-Z���_�.:Q�KTB��c������	ԑ
Yc��l�`�K��h0�5���NHq�1��59c�U���         _   x�3��x��7Y� ��Z$���B��y
�@�N���|����ëJ9��p��62DՕ��pw{�B��]3r/@5��1F�c��cR������ �]s�            x������ � �           x�m�AKCA�s���Yv�M��M��"z�"��l�K�Z����>��e``�W����%V��>/ẩ��޿�>��������t9>�ðHvFl��j#�fKr�aЈ\���p}���TQ|�e�����& �ѝa� �p�,ܺ���(Is�
r�!�����,>���^�l��Ǘr��z^�co�B�a��P�!Z�s
����<�-�@%ɡy+�`p5�����Y;E`6eG-@�Q�F�	�����T�:��L����f�     