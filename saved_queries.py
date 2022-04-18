q1 = {
    'description': """Quais Empresas Não Ativas na RFB mas Ativas na SEFAZ?""",
    'query': """PREFIX sefazma: <http://www.sefaz.ma.gov.br/ontology/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX vcard: <http://www.w3.org/2006/vcard/ns#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?estabelecimento_rfb ?nome_fantasia_rfb  WHERE {
  
  ?estabelecimento_rfb a sefazma:Estabelecimento_RFB;
     sefazma:nome_fantasia ?nome_fantasia_rfb;
     sefazma:tem_situacao_cadastral ?situacao_cadastral_rfb.
  ?situacao_cadastral_rfb sefazma:tipo_situacao ?tipo_situacao_rfb.
  
  ?estabelecimento_cadastro a sefazma:Estabelecimento_Cadastro;
     sefazma:tem_situacao_cadastral ?situacao_cadastral_cadastro.
  ?situacao_cadastral_cadastro sefazma:tipo_situacao ?tipo_situacao_cadastro.
    
  ?estabelecimento_rfb owl:sameAs  ?estabelecimento_cadastro.
 
  FILTER(?tipo_situacao_rfb != 'ATIVA')
  FILTER(?tipo_situacao_cadastro = 'ATIVA' && ?tipo_situacao_rfb != ?tipo_situacao_cadastro)

}
LIMIT 100""",
    'construct_query': """
    PREFIX sefazma: <http://www.sefaz.ma.gov.br/ontology/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX vcard: <http://www.w3.org/2006/vcard/ns#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

CONSTRUCT{
    ?estabelecimento_rfb sefazma:tem_situacao_cadastral ?situacao_cadastral_rfb.
    ?situacao_cadastral_rfb sefazma:tipo_situacao ?tipo_situacao_rfb.
    ?estabelecimento_cadastro sefazma:tem_situacao_cadastral ?situacao_cadastral_cadastro.
    ?situacao_cadastral_cadastro sefazma:tipo_situacao ?tipo_situacao_cadastro.
    ?estabelecimento_rfb owl:sameAs  ?estabelecimento_cadastro.
    ?estabelecimento_cadastro owl:sameAs ?estabelecimento_rfb.
    
}WHERE {
  
  ?estabelecimento_rfb a sefazma:Estabelecimento_RFB;
     sefazma:cnpj ?cnpj_estabelecimento_rfb;
     sefazma:nome_fantasia ?nome_fantasia_rfb;
     sefazma:tem_situacao_cadastral ?situacao_cadastral_rfb.
  
  ?situacao_cadastral_rfb sefazma:tipo_situacao ?tipo_situacao_rfb.
  
  ?estabelecimento_cadastro a sefazma:Estabelecimento_Cadastro;
      sefazma:cnpj ?cnpj_estabelecimento_cadastro;
      sefazma:nome_fantasia ?nome_fantasia_cadastro;
        sefazma:tem_situacao_cadastral ?situacao_cadastral_cadastro.
    
  ?situacao_cadastral_cadastro sefazma:tipo_situacao ?tipo_situacao_cadastro.
    
  ?estabelecimento_rfb owl:sameAs  ?estabelecimento_cadastro.
 
  FILTER(?tipo_situacao_rfb != 'ATIVA')
  FILTER(?tipo_situacao_cadastro = 'ATIVA' && ?tipo_situacao_rfb != ?tipo_situacao_cadastro)
    FILTER(?estabelecimento_rfb = <$URI>)
}
LIMIT 100
    """
}

# q2 = {
#     'description': """Quais Estabelecimentos contribuintes de ICMS da fonte Sefaz com CNPJ iguais e nomes diferentes (nome fantasia) na fonte RFB?""",
#     'query': """ PREFIX sefazma: <http://www.sefaz.ma.gov.br/ontology/>
# PREFIX foaf: <http://xmlns.com/foaf/0.1/>
# PREFIX owl: <http://www.w3.org/2002/07/owl#>
# PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
# PREFIX vcard: <http://www.w3.org/2006/vcard/ns#>
# PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

# SELECT ?cnpj_estabelecimento_rfb ?cnpj_estabelecimento_cadastro ?nome_fantasia_rfb ?nome_fantasia_cadastro where { 
#   ?estabelecimento_rfb a sefazma:Estabelecimento_RFB;
#      sefazma:cnpj ?cnpj_estabelecimento_rfb;
#      sefazma:nome_fantasia ?nome_fantasia_rfb.
  
#   ?estabelecimento_cadastro a sefazma:Estabelecimento_Cadastro;
#       sefazma:cnpj ?cnpj_estabelecimento_cadastro;
#       sefazma:nome_fantasia ?nome_fantasia_cadastro.
    
#  ?estabelecimento_rfb owl:sameAs  ?estabelecimento_cadastro.
    
#    FILTER(?nome_fantasia_rfb != ?nome_fantasia_cadastro) 
# } LIMIT 100"""
# }
saved_queries = [q1]