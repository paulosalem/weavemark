# Recurring Topic Monitor Trace — child-events

- Model: `gpt-5.5`
- Spec: `promplets/catalog/executable/recurring-topic-monitor.weavemark.md`
- Companion runtime: `examples/python-runtime-integrations/recurring-topic-monitor/run.py`
- Tool providers:
  - `ellements.standard_tools.web.search`
  - `ellements.standard_tools.web.crawler`

## Variables

```json
{
  "topic": "things to do with my 6 y.o. child",
  "age": 6,
  "monitor_mode": "events",
  "cadence": "weekly",
  "lookback_window": "next 7 days",
  "region": "São Paulo, Brazil",
  "audience": "a parent looking for practical, age-appropriate activities",
  "research_depth": "deep",
  "run_date": "today",
  "previous_run_context": "No previous run context supplied.",
  "user_constraints": "Prefer safe, age-appropriate, not-too-expensive activities. Include booking, weather, location, cost, and age-fit caveats when available.",
  "seed_urls": [
    "https://www.sescsp.org.br/programacao/cores-e-caras-mascaras-infantis",
    "https://www.sescsp.org.br/programacao/territorio-do-brincar-3",
    "https://www.sescsp.org.br/programacao/do-piao-a-pipa-brincadeiras-de-rua-projeto-de-ferias-sesc-belenzinho",
    "https://saopauloparacriancas.com.br"
  ],
  "companion_runtime_results": "Injected by the companion runtime after Ellements web search, news search, first-level crawling, and second-level crawling.",
  "seed_urls_summary": "- https://www.sescsp.org.br/programacao/cores-e-caras-mascaras-infantis\n- https://www.sescsp.org.br/programacao/territorio-do-brincar-3\n- https://www.sescsp.org.br/programacao/do-piao-a-pipa-brincadeiras-de-rua-projeto-de-ferias-sesc-belenzinho\n- https://saopauloparacriancas.com.br"
}
```

## Compiled prompt

```markdown
You are a rigorous analytical assistant running a recurring deep web monitor. Produce evidence-grounded, clearly structured, actionable analysis for a parent looking for practical, age-appropriate activities.

# Recurring Topic Monitor

## Monitor parameters

- Topic: things to do with my 6 y.o. child
- Child age: 6
- Mode: events
- Cadence: weekly
- Lookback window: next 7 days
- Region or location: São Paulo, Brazil
- Audience: a parent looking for practical, age-appropriate activities
- Depth: deep
- Run date: today
- Previous-run context: No previous run context supplied.
- User constraints: Prefer safe, age-appropriate, not-too-expensive activities. Include booking, weather, location, cost, and age-fit caveats when available.
- Source seeds:
  - https://www.sescsp.org.br/programacao/cores-e-caras-mascaras-infantis
  - https://www.sescsp.org.br/programacao/territorio-do-brincar-3
  - https://www.sescsp.org.br/programacao/do-piao-a-pipa-brincadeiras-de-rua-projeto-de-ferias-sesc-belenzinho
  - https://saopauloparacriancas.com.br

## Companion runtime evidence

The companion runtime will inject web search, news search, crawl, and second-level crawl results here before final synthesis:

Injected by the companion runtime after Ellements web search, news search, first-level crawling, and second-level crawling.

## Research status and context sufficiency

Before ranking activities, classify the available context as sufficient, limited, or insufficient.

For this run, judge sufficiency using these dimensions:
- whether the runtime evidence covers São Paulo, Brazil and the next 7 days;
- whether each candidate has date, time, location, booking or access details, cost, age suitability, weather or indoor/outdoor caveats, and source provenance;
- whether the evidence includes official or primary event pages where possible;
- whether source seeds were crawled and checked rather than assumed reliable;
- whether inaccessible, stale, duplicate, off-topic, or thin pages were rejected;
- whether the safety, cost, distance, eligibility, and scheduling implications are clear enough for a parent to act.

If context is limited, provide a bounded digest with visible caveats. If context is insufficient, avoid confident recommendations, identify the missing inputs, and provide the smallest next searches or crawls needed to proceed.

## Tool and runtime contract

Use the Ellements-backed tools available to the runtime:
- search_web for current web information about activities and event listings;
- search_news for current news or announcement-style sources when useful;
- crawl_url to inspect official event pages, venue pages, local calendars, seed URLs, and high-signal links.

Do not rely on search snippets alone when a crawl is available and the item may affect a parent’s decision. Preserve source title, URL, date if available, and whether the evidence came from search results, first-level crawl, or second-level crawl.

## Required research behavior

Treat the exact topic as the monitoring target: things to do with a 6-year-old child in São Paulo, Brazil during the next 7 days. Do not broaden it unless a broader query is explicitly marked as discovery support.

Because the mode is events:
- prioritize upcoming or currently available events and activities;
- include date, time, location, booking link, cost, eligibility or age fit, practical notes, and why each item fits the topic;
- exclude past events unless the next occurrence is clear;
- exclude vague activity ideas without a source or availability;
- exclude items unsuitable for a 6-year-old, the user constraints, or the region.

Because the research depth is deep:
- use broad query families;
- crawl selected first-level sources;
- extract high-signal links from first-level pages;
- crawl selected second-level sources when they improve evidence quality;
- perform contradiction checks;
- include a detailed source map.

Search several source families:
1. Recent or breaking listings and announcements inside the lookback window.
2. Primary or official sources such as venue calendars, organizers, museums, SESC pages, municipal cultural calendars, parks, theaters, and booking pages.
3. Expert or practitioner sources where relevant, such as child-focused cultural guides or family activity curators.
4. Local or domain-specific calendars, especially São Paulo family and children’s activity listings.
5. Skeptical or contrary sources for cancellation, safety concerns, access limitations, weather disruption, overcrowding, or age mismatch.
6. Source-rich roundups that point to multiple primary listings.

Treat source seeds as starting points, not conclusions. Crawl them, check recency and relevance, reject stale or off-topic pages, and continue searching beyond them when evidence is thin.

Deduplicate repeated stories, reposted listings, mirrored event pages, repeated venue calendar entries, and low-signal aggregators. Rank by user relevance, novelty, evidence quality, timeliness, practical actionability, cost fit, safety, and age appropriateness.

Stop crawling when additional pages are redundant, stale, inaccessible, lower value than sources already read, or unlikely to improve evidence quality. The goal is deeper evidence, not more pages.

## Evidence and reasoning standards

Separate facts, reported claims, assumptions, opinions, forecasts, and speculation. Do not fabricate citations, URLs, dates, quotes, source names, costs, booking details, or age guidance.

Preserve dates, names, locations, URLs, costs, age guidance, source titles, proper nouns, quotations, and provenance exactly when available. Use program and programming instead of code and coding in authored prose, while preserving exact source titles, proper nouns, quotations, and URLs.

For each material recommendation, provide:
- the strongest source link and source type;
- the evidence basis;
- confidence level as high, medium, or low;
- the strongest caveat or counter-argument;
- what a parent should verify before acting.

Evaluate evidence quality using:
- relevance: direct support versus adjacent or generic material;
- specificity: concrete facts, dates, costs, booking details, and location versus vague assertions;
- freshness: current enough for the next 7 days;
- independence: multiple independent sources versus repeated source families;
- contradictions: whether tensions, cancellations, stale data, or conflicting details are surfaced.

End the evidence assessment with:
- evidence grade: strong, adequate, weak, or insufficient;
- main gap: the missing evidence that most limits confidence;
- decision impact: whether the parent can act, should verify, should wait, or should investigate.

## News and event presentation quality

For any news-derived or announcement-style item, include relevant context, timelines, named entities, benefits, risks, affected people, and why it matters now. Avoid sensationalism, shallow summaries, boilerplate, and false confidence.

For events and activities, make the digest practically useful:
- what is happening;
- why it fits a 6-year-old;
- where and when it happens;
- how to book or attend;
- expected cost or whether cost is unavailable;
- weather, indoor/outdoor, travel, safety, language, accessibility, and age-fit caveats;
- a practical next step.

## Recurring-monitor behavior

Make the digest useful for a weekly recurring run:
- explain what appears new inside the lookback window;
- identify still-important items that remain actionable;
- compare against previous-run context when supplied;
- since no previous run context is supplied, identify what appears new within the lookback window and mark the comparison as limited;
- record omissions and monitoring gaps so a future run can compare what changed;
- include sources, organizations, venues, queries, and signals to monitor next.

## Explainability requirements

Start important sections with the conclusion or recommendation, then show the reasoning chain. For ranked findings, include a compact explanation of:
- claim or inference;
- evidence or basis;
- confidence;
- key assumptions;
- checks performed;
- limits;
- simplest plain-language explanation.

## Output requirements

Return only a Markdown digest with these sections:

1. Monitor snapshot — topic, child age, mode, cadence, lookback window, region, run date, research status, context status, and evidence grade.
2. Top findings — ranked list of the most relevant events or activities. Each item must include why it matters, source link, date and time if available, location, cost if available, booking or attendance step, age-fit notes for a 6-year-old, confidence, caveats, and practical next step.
3. Source map — query families searched, sources crawled, second-level sources crawled, strongest sources, weak or rejected sources, and gaps.
4. What changed or what is new — compare against previous-run context when supplied; otherwise identify what appears new within the lookback window and state that the comparison is limited.
5. Contradictions, caveats, and missing evidence — include source conflicts, inaccessible pages, stale data, uncertain costs, booking uncertainty, age-fit uncertainty, weather concerns, or safety/accessibility caveats.
6. Watchlist for next run — queries, sources, organizations, venues, companies, people, calendars, or signals to monitor next.
7. Action checklist — subscribe, read, book, verify, attend, ignore, or follow up, depending on the user constraints and the evidence.

Use clear headings, concise bullets, and source-grounded language. Put caveats near the relevant recommendation, not only at the end.
```

## Companion runtime results

```json
{
  "run_timestamp": "2026-07-05T14:41:46.929109+00:00",
  "settings": {
    "topic": "things to do with my 6 y.o. child",
    "monitor_mode": "events",
    "cadence": "weekly",
    "lookback_window": "next 7 days",
    "region": "São Paulo, Brazil",
    "audience": "a parent looking for practical, age-appropriate activities",
    "research_depth": "deep",
    "max_results_per_query": 7,
    "max_first_level_sources": 6,
    "max_second_level_sources": 4,
    "age": "6",
    "user_constraints": "Prefer safe, age-appropriate, not-too-expensive activities. Include booking, weather, location, cost, and age-fit caveats when available.",
    "seed_urls": [
      "https://www.sescsp.org.br/programacao/cores-e-caras-mascaras-infantis",
      "https://www.sescsp.org.br/programacao/territorio-do-brincar-3",
      "https://www.sescsp.org.br/programacao/do-piao-a-pipa-brincadeiras-de-rua-projeto-de-ferias-sesc-belenzinho",
      "https://saopauloparacriancas.com.br"
    ]
  },
  "query_plan": [
    {
      "label": "upcoming_events",
      "tool": "search_web",
      "query": "programação infantil crianças 6 anos São Paulo próximos 7 dias fim de semana",
      "time_range": "d"
    },
    {
      "label": "official_calendars",
      "tool": "search_web",
      "query": "site:sescsp.org.br/programacao programação infantil crianças São Paulo",
      "time_range": "d"
    },
    {
      "label": "venue_calendars",
      "tool": "search_web",
      "query": "site:cataventocultural.org.br programação férias crianças São Paulo",
      "time_range": "d"
    },
    {
      "label": "city_culture_calendar",
      "tool": "search_web",
      "query": "site:capital.sp.gov.br cultura programação infantil crianças São Paulo",
      "time_range": "d"
    },
    {
      "label": "local_roundups",
      "tool": "search_web",
      "query": "São Paulo para crianças programação infantil fim de semana férias museu teatro",
      "time_range": "d"
    },
    {
      "label": "age_fit_safety",
      "tool": "search_web",
      "query": "crianças 6 anos São Paulo gratuito ingresso atividade infantil segura",
      "time_range": "d"
    },
    {
      "label": "cancellations_changes",
      "tool": "search_news",
      "query": "programação infantil São Paulo cancelamento alteração chuva crianças",
      "time_range": "d"
    }
  ],
  "seed_urls": [
    "https://www.sescsp.org.br/programacao/cores-e-caras-mascaras-infantis",
    "https://www.sescsp.org.br/programacao/territorio-do-brincar-3",
    "https://www.sescsp.org.br/programacao/do-piao-a-pipa-brincadeiras-de-rua-projeto-de-ferias-sesc-belenzinho",
    "https://saopauloparacriancas.com.br"
  ],
  "search_results": {
    "upcoming_events": {
      "query": "programação infantil crianças 6 anos São Paulo próximos 7 dias fim de semana",
      "results": [
        {
          "title": "A melhor programação infantil para o fim de semana em São Paulo !",
          "url": "https://www.justrealmoms.com.br/a-melhor-programacao-infantil-para-o-fim-de-semana-em-sao-paulo-por-bora-ai1/",
          "snippet": "Programação para crianças em São Paulo – por bora.ai.Pensei na semana passada em escrever sobre o Carnaval. Achei muito óbvio e muito pequeno para o que se passa aqui dentro do meu coração.",
          "source": "google"
        },
        {
          "title": "Natal Iluminado, samba e circo marcam o fim de semana em São Paulo",
          "url": "https://osaopaulo.org.br/sao-paulo/natal-iluminado-samba-e-circo-marcam-o-fim-de-semana-em-sao-paulo/",
          "snippet": "A agenda cultural paulistana deste fim de semana , dias 6 e 7 de dezembro, tem intensa programação . A celebração da cultura negra e do samba é o grande destaque.",
          "source": "google"
        },
        {
          "title": "Programação Infantil com Fabulosos anima os fins de semana de...",
          "url": "https://blog.bondinho.com.br/programacao-infantil-parque-bondinho-agosto-2025/",
          "snippet": "Programação infantil com Fabulosos no Parque Bondinho Pão de Açúcar.Diversão e aprendizado para as crianças . A cada fim de semana , os pequenos têm a oportunidade de participar de pocket shows interativos, oficinas criativas e contações de histórias que estimulam a fantasia.",
          "source": "google"
        },
        {
          "title": "Fim de Semana das Crianças – Via Brasil Shopping *11 e 12 de...",
          "url": "https://roteirinhocarioca.com.br/2025/01/01/fim-de-semana-das-criancas-via-brasil-shopping/",
          "snippet": "As atrações serão divididas por dia : *oficinas: limite de 50 crianças por tema. Classificação – Livre. Via Brasil Shopping Rua Itapera, 500/2º piso – Irajá. Sábado, das 15h às 19h e domingo, das 13h às 18h Gratuito Dias 11 e 12 de outubro de 2025.",
          "source": "google"
        },
        {
          "title": "Fim de semana em Brasília - 15, 16 e 17/04/2016",
          "url": "https://maesbrasileiras.com.br/fim-de-semana-em-brasilia/",
          "snippet": "Além disso, crianças de até 3 anos poderão se entreter com produtos Playskool ou colorir os queridinhos DohDoh’s. Para finalizar, um painel de fotos divertido e decorado com potes gigantes da massinha Play-Doh promete registrar a brincadeira para recordação das crianças .",
          "source": "google"
        },
        {
          "title": "Maguje Recebe Fabulosos com Programação Infantil nos Almoços...",
          "url": "https://revistadegusta.com/maguje-recebe-fabulosos-com-programacao-infantil-nos-almocos-de-fim-de-semana/",
          "snippet": "No fim de semana , dedicado ao Dia das Crianças (12 e 13), uma Oficina de Slime, que é febre no momento, vai divertir a criançada. No próximo fim de semana (19 e 20), o espaço vai contar com Sarauzinho e, nos dias 26 e 27, Halloween para os pequenos.",
          "source": "google"
        },
        {
          "title": "Arp de Portas Abertas acontece neste fim de semana dedicado ao Dia ...",
          "url": "https://descubranovafriburgo.com.br/arp-de-portas-abertas-acontece-neste-fim-de-semana-dedicado-ao-dia-dos-pais/",
          "snippet": "Aliás, a programação infantil está completa com, além das oficinas, brinquedos gratuitos, pagos e o Espaço Kids, nova área dedicada a receber toda a energia da garotada. Fotos: Thalles Kadett.",
          "source": "google"
        }
      ],
      "total_results": 7,
      "query_family": "upcoming_events",
      "query_tool": "search_web"
    },
    "official_calendars": {
      "query": "site:sescsp.org.br/programacao programação infantil crianças São Paulo",
      "results": [
        {
          "title": "Confira a programação infantil de janeiro no Sesc Avenida Paulista...",
          "url": "https://www.sescsp.org.br/editorial/confira-a-programacao-infantil-de-janeiro-no-sesc-avenida-paulista/",
          "snippet": "Em janeiro, a programação voltada ao público infantil ocupará diferentes espaços da unidade, com atividades que contemplam não só as crianças , como toda a família. Confira a programação completa",
          "source": "google"
        },
        {
          "title": "Programação - Sesc São Paulo",
          "url": "https://www.sescsp.org.br/programacao/territorio-do-brincar-3/",
          "snippet": "No Território do Brincar, bebês e crianças até 6 anos são convidados a explorar, imaginar e descobrir o mundo por meio de experiências sensoriais, brincadeiras e encontros afetivos.",
          "source": "google"
        },
        {
          "title": "Já tem programação para este fim de semana? Vem pro Sesc...",
          "url": "https://www.sescsp.org.br/ja-tem-programacao-para-este-fim-de-semana-vem-pro-sesc-avenida-paulista/?buscar_curso=0&palavra&unidade_id=2&ATIVIDADE_ID=0&data2=0",
          "snippet": "Confira a programação infantil de fevereiro no Sesc Avenida Paulista. Em fevereiro, a programação voltada ao público infantil segue a todo vapor, ocupando diferentes espaços da unidade.",
          "source": "google"
        },
        {
          "title": "Conheça a programação do Sesc na Semana da Criança - Sesc São ...",
          "url": "https://www.sescsp.org.br/editorial/conheca-a-programacao-do-sesc-na-semana-da-crianca/",
          "snippet": "No feriado do dia 12, às 15h, a Cia. Trucks apresenta o espetáculo teatral infantil Isso é coisa de Criança , com transmissão ao vivo pelo canal do YouTube do Sesc São Paulo , pelo Crianças #EmCasaComSesc.",
          "source": "google"
        },
        {
          "title": "Confira a programação infantil de fevereiro no Sesc Avenida Paulista...",
          "url": "https://www.sescsp.org.br/editorial/confira-a-programacao-infantil-de-fevereiro-no-sesc-avenida-paulista/",
          "snippet": "Em fevereiro, a programação voltada ao público infantil do Sesc Avenida Paulista segue a todo vapor, ocupando diferentes espaços da unidade. São brincadeiras, atividades esportivas, espetáculo de circo, oficinas, contação de histórias e uma programação de Carnaval pra toda família.",
          "source": "google"
        },
        {
          "title": "Programação - Sesc São Paulo",
          "url": "https://www.sescsp.org.br/programacao/do-piao-a-pipa-brincadeiras-de-rua-projeto-de-ferias-sesc-belenzinho/",
          "snippet": "Para encerrar a semana, teremos uma saída para o Museu do Ipiranga onde as crianças experimentarão uma descida de carrinho de rolimã em um dos pontos mais famosos da cidade de São Paulo . ( Programação sujeita a alterações em função das condições climáticas).",
          "source": "google"
        }
      ],
      "total_results": 6,
      "query_family": "official_calendars",
      "query_tool": "search_web"
    },
    "venue_calendars": {
      "query": "site:cataventocultural.org.br programação férias crianças São Paulo",
      "results": [
        {
          "title": "São Paulo All Inclusive - Férias em família",
          "url": "https://www.bing.com/aclick?ld=e8L0hj0Z8Qh2PPrhyNFh1YXDVUCUyAQ1dzP7_aaewe00XVArKS3GISHMmSk6VoFxM85bCTRmSCKZK595FX0snPalRSQCSYdEuDMeFVmvZIrFdaBW5b7VGxWAE5q2spPHHYcWwOTHBOn5luis-8DhGpI4pbdiNOKkt1L3npiDjjcv4eCrlBTIT52FkPFitYCwJqwE0cTXd78z4wMsywRM_UQPBwKO0&u=aHR0cHMlM2ElMmYlMmZhZC5kb3VibGVjbGljay5uZXQlMmZzZWFyY2hhZHMlMmZsaW5rJTJmY2xpY2slM2ZsaWQlM2Q0MzcwMDA4MDE2ODU4Nzg5MiUyNmRzX3Nfa3dnaWQlM2Q1ODcwMDAwODcxODIxODE3MCUyNmRzX2FfY2lkJTNkMTM0NzM2OTExJTI2ZHNfYV9jYWlkJTNkNjk4MTg5NTgxJTI2ZHNfYV9hZ2lkJTNkMTI0MjQ0OTQ1OTYwMDE5MiUyNmRzX2FfZmlpZCUzZCUyNmRzX2FfbGlkJTNka3dkLTc3NjUzNDUwOTg2NTA5JTNhbG9jLTIwJTI2ZHNfYV9leHRpZCUzZCU3YmV4dGVuc2lvbmlkJTdkJTI2JTI2ZHNfZV9hZGlkJTNkJTI2ZHNfZV9tYXRjaHR5cGUlM2RzZWFyY2glMjZkc19lX2RldmljZSUzZGMlMjZkc19lX25ldHdvcmslM2RvJTI2JTI2ZHNfdXJsX3YlM2QyJTI2ZHNfZGVzdF91cmwlM2RodHRwcyUzYSUyZiUyZnd3dy5jbHVibWVkLmNvbS5iciUyZiUzZmdjbHNyYyUzZDNwLmRzJTI2JTI2bXNjbGtpZCUzZGVlOTFiMTE5ODVmMTE1ZWY3ZTZhZGI1M2U4ZjJiMWY5JTI2dXRtX3NvdXJjZSUzZGJpbmclMjZ1dG1fbWVkaXVtJTNkY3BjJTI2dXRtX2NhbXBhaWduJTNkU0VBX0dOX1JFR0lfQlJBU0lMX0JaX1BUJTI2dXRtX3Rlcm0lM2RyZXNvcnQlMjUyMGFsbCUyNTIwaW5jbHVzaXZlJTI1MjBzYW8lMjUyMHBhdWxvJTI2dXRtX2NvbnRlbnQlM2RTJWMzJWEzbyUyNTIwUGF1bG8&rlid=ee91b11985f115ef7e6adb53e8f2b1f9",
          "snippet": "Garanta seu All Inclusive em São Paulo com atividades adaptadas a cada membro da família. Para se divertir ou relaxar | Reserve agora com Club Med",
          "source": "auto"
        }
      ],
      "total_results": 1,
      "query_family": "venue_calendars",
      "query_tool": "search_web"
    },
    "city_culture_calendar": {
      "query": "site:capital.sp.gov.br cultura programação infantil crianças São Paulo",
      "results": [
        {
          "title": "Programação Mensal 2025 - Secretaria Municipal do Verde e do Meio...",
          "url": "https://capital.sp.gov.br/web/meio_ambiente/w/umapaz/programacao_mensal/345",
          "snippet": "Horário: 09:00 às 12:00. Oficina Presencial Casa Verde/Cachoeirinha. A oficina \"Brincando com a Natureza\" é uma atividade lúdica e educativa voltada para crianças da educação infantil , que visa promover a interação com o meio ambiente por meio de brincadeiras e atividades práticas.",
          "source": "google"
        },
        {
          "title": "Programação da Jornada do Patrimônio 2024 - Secretaria Municipal...",
          "url": "https://capital.sp.gov.br/web/cultura/w/patrimonio_historico/jornada_do_patrimonio/programacao/35790",
          "snippet": "Cursos: Programação Educação Ambiental: Circuito Biodiversidade no Coração de São Paulo (Parque Ibirapuera). Urbia Data: 17/08. Local: Parque do Ibirapuera - Início no centro de visitantes, próximo ao Planetário Ibirapuera.",
          "source": "google"
        },
        {
          "title": "Biblioteca Viva - Secretaria Municipal de Cultura e Economia Criativa...",
          "url": "https://capital.sp.gov.br/web/cultura/w/bibliotecas/programas_projetos/21630",
          "snippet": "Prefeitura de São Paulo Logo da Secretaria Municipal de Cultura .O programa Biblioteca Viva busca revitalizar as bibliotecas municipais de São Paulo , apostando no papel cultural do livro e na importância do incentivo à leitura na formação dos cidadãos paulistanos.",
          "source": "google"
        },
        {
          "title": "Agenda restauro - Secretaria Municipal de Cultura e Economia...",
          "url": "https://capital.sp.gov.br/web/cultura/w/agendarestauro-1",
          "snippet": "Prefeitura de São Paulo Logo da Secretaria Municipal de Cultura e Economia Criativa.",
          "source": "google"
        },
        {
          "title": "Serviços - IPTU 2025 - Prefeitura",
          "url": "https://capital.sp.gov.br/web/iptu2025/serviços",
          "snippet": "Logo da Cidade de São Paulo : A imagem mostra o brasão da Cidade de São Paulo . O brasão contém armas da cidade, em verde e branco, com uma coroa na parte superior.",
          "source": "google"
        },
        {
          "title": "Confira a publicação do Plano de Salvaguarda do Teatro de Grupo de...",
          "url": "https://capital.sp.gov.br/web/cultura/w/planodesalvaguardadoteatrodegruposp",
          "snippet": "Entre as iniciativas previstas, está a valorização do teatro como espaço de memória e transformação social, além da promoção de sua relevância na identidade cultural de São Paulo .",
          "source": "google"
        }
      ],
      "total_results": 6,
      "query_family": "city_culture_calendar",
      "query_tool": "search_web"
    },
    "local_roundups": {
      "query": "São Paulo para crianças programação infantil fim de semana férias museu teatro",
      "results": [
        {
          "title": "Ingressos para Shows, Teatros e outros eventos - EVENTIM",
          "url": "https://www.eventim.com.br/city/sao-paulo-943/this-month/",
          "snippet": "14 hours ago · Lorelay Fox em São Paulo ! Espetáculo em temporada de 29/04 a 15/07/2026 no Teatro Youtube. Garanta seu ingresso e não perca essa apresentação imperdível ao vivo. 08/07/2026 ─ 22/07/20263 eventos Show all 3 eventos São Paulo , qua. 08/07/2026, 20:00 LORELIVE Comprar São Paulo , qua. 22/07/2026, 20:00 LORELIVE Comprar TRIBUTO BOB DYLAN - MARCELO PAIVA E LUÍZA VILLA 08/07/20261 evento ...",
          "source": "google"
        },
        {
          "title": "Grade de programação - TV Cultura",
          "url": "https://cultura.uol.com.br/grade/06072026.html",
          "snippet": "Jul 6, 2026 · Mas para Helena o mar e a areia são mais do que um local de férias , são seu lar sagrado. Seus familiares vivem lá na Ilha do Cajual, no Maranhão, sob a luz e proteção de Iemanjá. Aproveite as ondas e conchinas da praia junto a essa Espinossaura Mascava, que sob o sol descansa embalada pelos versos de Camões.",
          "source": "google"
        },
        {
          "title": "O que fazer com as crianças durante o fim de semana em São Paulo ?",
          "url": "https://www.justrealmoms.com.br/o-que-fazer-com-criancas-fim-de-semana-sao-paulo/",
          "snippet": "Mais uma vez, o bora.ai fez uma seleção com a melhor programação infantil em São Paulo . Durante o final de semana , a capital paulista vai receber várias atrações que vão deixar os pequenos malucos (no bom sentido, é claro!).",
          "source": "google"
        },
        {
          "title": "Programação para as crianças nas férias | VEJA SÃO PAULO",
          "url": "https://vejasp.abril.com.br/cultura-lazer/programacao-criancas-ferias/",
          "snippet": "Para fechar a programação , o próprio Ossamá fará uma apresentação neste sábado (2), às 18h, convidando a plateia a participar de seus truques. A exposição é gratuita e pode ser vista de segunda a sábado, das 10h às 22h.",
          "source": "google"
        },
        {
          "title": "No fim de semana , atrações convidam os pequenos... - Guia Folha",
          "url": "https://guia.folha.uol.com.br/crianca/2019/07/no-fim-de-semana-atracoes-convidam-os-pequenos-a-soltarem-a-voz.shtml",
          "snippet": "No fim de semana , duas atrações convidam a criançada a brincar e fazer barulho. Banda Mirim O coletivo, formado por 12 atores, apresenta um show para crianças , no qual mesclam linguagens de circo, teatro e música...",
          "source": "google"
        },
        {
          "title": "FÉRIAS no MAM - Museu de Arte Moderna com programação infantil",
          "url": "https://sampacomcriancas.com.br/ferias-no-mam-museu-de-arte-moderna-com-programacao-infantil/",
          "snippet": "Participantes: 25 pessoas ( crianças e acompanhantes). Descrição: A partir da técnica de colagem, os participantes são convidados a explorar um universo de narrativas inspiradas na exposição Livro de Artista, em exibição no MAM, na Sala Paulo Figueiredo. Duração: 60 minutos.",
          "source": "google"
        },
        {
          "title": "Fim de semana em São Paulo - 04, 05, 11 e 12 de Outubro",
          "url": "https://maesbrasileiras.com.br/fim-de-semana-em-sao-paulo-04-05-11-e-12-de-outubro/",
          "snippet": "O dia das crianças está se aproximando e a Daslu Boys & Girls convida seus clientes para trazerem seus filhos para uma tarde de customização. O evento acontecerá nos próximos sábados, 4/09 e 11/09, na Daslu do Shopping JK e Shopping Cidade Jardim.",
          "source": "google"
        }
      ],
      "total_results": 7,
      "query_family": "local_roundups",
      "query_tool": "search_web"
    },
    "age_fit_safety": {
      "query": "crianças 6 anos São Paulo gratuito ingresso atividade infantil segura",
      "results": [
        {
          "title": "Brasil Ingressos - 365 Tickets",
          "url": "https://www.365tickets.com.br/dock/team/brazil",
          "snippet": "14 hours ago · São cinco títulos — 1958, 1962, 1970, 1994 e 2002 — e uma lista de craques que encantaram os gramados: Pelé, Garrincha, Zico, Romário, Ronaldo, Ronaldinho e Neymar. A camisa amarela é a mais icônica do futebol mundial, e a expectativa que acompanha o ato de vesti-la é incomparável.",
          "source": "google"
        },
        {
          "title": "Atividade Conjunto Educação Infantil — BSYSTEM",
          "url": "https://dev.cg.no/ihn/atividade-conjunto-educao-infantil",
          "snippet": "Quantas crianças participam de uma atividade conjunto educação infantil ideal? Geralmente, grupos de 2 a 6 crianças funcionam melhor, pois permitem participação ativa e facilitam a mediação. E se surgir conflitos durante a atividade ?",
          "source": "google"
        },
        {
          "title": "Lugares Para Ir Em Sao Paulo A Noite Gratuito | TikTok",
          "url": "https://www.tiktok.com/discover/lugares-para-ir-em-sao-paulo-a-noite-gratuito",
          "snippet": "-A partir de 12 anos . ATENÇÃO: Cada criança deve ter um adulto responsável durante o passeio na represa. Se você for com 2 ou mais crianças , não poderá levar todas ao mesmo tempo na atividade .",
          "source": "google"
        },
        {
          "title": "DESCONTO. Atrações em São Paulo | Sampa com Crianças",
          "url": "https://sampacomcriancas.com.br/desconto-atracoes-em-sao-paulo/",
          "snippet": "Atrações em São Paulo . by Sampa com Crianças . Ingresso adulto R$ 44,90 e infantil R$ 64,90 e Combo (1 adulto + 1 infantil ) R$ 70. Crianças a partir de 2 anos pagam ingressos .",
          "source": "google"
        },
        {
          "title": "Mesa Infantil Segura Para Criança - Monte Líbano... - Magazine Luiza",
          "url": "https://www.magazineluiza.com.br/mesa-infantil-segura-para-crianca-monte-libano/p/chdfc37hea/br/meti/?seller_id=bruputilidades",
          "snippet": "Magazine Luiza. Imagem de Mesa Infantil Segura Para Criança . thumbnails-0.Transforme o momento de estudo e brincadeira em uma experiência divertida e organizada com a Mesa Infantil de Ensino Para Menina Tema Unicórnio.",
          "source": "google"
        },
        {
          "title": "Ingresso .com - Aqui começa o seu momento!",
          "url": "https://www.ingresso.com/",
          "snippet": "Confira o que está em cartaz no cinema, os melhores espetáculos e notícias.",
          "source": "google"
        },
        {
          "title": "PARABÉNS DA GALINHA PINTADINHA - Clipe Música... - YouTube",
          "url": "https://www.youtube.com/watch?v=ei2-RjJDBHc",
          "snippet": "Músicas infantil .",
          "source": "google"
        }
      ],
      "total_results": 7,
      "query_family": "age_fit_safety",
      "query_tool": "search_web"
    },
    "cancellations_changes": {
      "query": "programação infantil São Paulo cancelamento alteração chuva crianças",
      "results": [
        {
          "title": "Programação infantil em São Paulo - por bora.ai - Just Real Moms",
          "url": "https://www.justrealmoms.com.br/programacao-infantil-em-sao-paulo/",
          "snippet": "Vem ver a melhor programação com o que vai rolar em São Paulo ! Não fique de fora !O projeto visa desacelerar as crianças do universo digital e tecnológico, oferecendo brincadeiras tradicionais, contato com a natureza e com outras crianças .",
          "source": "google"
        },
        {
          "title": "Programação infantil do Sesc Santo André em fevereiro ABC do ABC",
          "url": "https://abcdoabc.com.br/programacao-infantil-sesc-santo-andre-fevereiro/",
          "snippet": "Ao longo de fevereiro, o Sesc Santo André apresenta uma programação infantil que ocupa diferentes espaços da unidade, reunindo atividades gratuitas e espetáculos pensados para bebês, crianças e famílias.",
          "source": "google"
        },
        {
          "title": "Sesc de São Paulo tem programação infantil especial para... - eCycle",
          "url": "https://www.ecycle.com.br/sesc-de-sao-paulo-tem-programacao-infantil-especial-para-o-mes-do-meio-ambiente/",
          "snippet": "Além da programação em rede, o projeto conta com a 10ª Conferência Internacional de Educação Ambiental e Sustentabilidade – o melhor de ambos os mundos (Best of Both Worlds), que acontece no Sesc Sorocaba entre os dias 12 a 15 de junho.",
          "source": "google"
        },
        {
          "title": "Carnaval infantil em Fortaleza: onde curtir com as crianças",
          "url": "https://www.opovo.com.br/vidaearte/carnaval/2026/02/12/carnaval-infantil-em-fortaleza-veja-onde-curtir-com-as-criancas.html",
          "snippet": "Acompanhe a programação do Carnaval infantil em Fortaleza durante o Ciclo Carnavalesco de 2026 (de 14/02 a 17/02).Desta sexta-feira, 13, até terça-feira, 17, praças, shoppings e equipamentos culturais oferecem uma programação especial gratuita que vai levar a folia para todos.",
          "source": "google"
        },
        {
          "title": "Shopping de São Paulo tem programação infantil com contação de...",
          "url": "https://www.culturasemcensura.com.br/2025/03/shopping-de-sao-paulo-tem-programacao.html",
          "snippet": "Contação de histórias no Shopping Penha. Programação : Dia 22 de março - história ‘Quando a Lua Tomou Chá de Sumiço’. Dia 29 de março - história ‘Ceci: uma história para ouvir’. Horário: sempre às 15h. Local: praça de alimentação. Programação gratuita e disponível ao público.",
          "source": "google"
        },
        {
          "title": "Alteração , cancelamento e reembolso de voo: como fazer?",
          "url": "https://www.voetranquilo.com/blog/alteracao-cancelamento-e-reembolso-de-voo-como-fazer/",
          "snippet": "Precisa fazer uma alteração ou cancelamento de voo e pedir o reembolso? Entenda como fazer isso e veja as taxas cobradas pelas companhias!",
          "source": "google"
        },
        {
          "title": "PARABÉNS DA GALINHA PINTADINHA - Clipe Música... - YouTube",
          "url": "https://www.youtube.com/watch?v=ei2-RjJDBHc",
          "snippet": "Músicas infantil .",
          "source": "google"
        }
      ],
      "total_results": 7,
      "fallback_from": "search_news",
      "fallback_reason": "News search failed: No results found.",
      "query_family": "cancellations_changes",
      "query_tool": "search_news"
    }
  },
  "crawl_rounds": {
    "first_level": [
      {
        "level": "1",
        "url": "https://www.sescsp.org.br/programacao/cores-e-caras-mascaras-infantis",
        "markdown": "[![Logo do Sesc](https://www.sescsp.org.br/wp-content/plugins/sesc-menu/src/assets/logo.svg)](https://www.sescsp.org.br)\nInstitucional![Mini ícone de um triângulo, indicando se a lista de links está aberta ou fechada.](https://www.sescsp.org.br/wp-content/plugins/sesc-menu/src/assets/new-caret.svg)\nUnidades![Mini ícone de um triângulo, indicando se a lista de links está aberta ou fechada.](https://www.sescsp.org.br/wp-content/plugins/sesc-menu/src/assets/new-caret.svg)\n![close-button](https://www.sescsp.org.br/wp-content/plugins/sesc-menu/src/assets/close.svg)\n![Ícone de configurações, com três barras horizontais paralelas, representando o 'menu sanduíche'.](https://www.sescsp.org.br/wp-content/plugins/sesc-menu/src/assets/sandwich.svg)\n[ Sobre o Sesc ](https://portal.sescsp.org.br/pt/sobre-o-sesc/)\n[ Oportunidades de Trabalho ](https://www.sescsp.org.br/oportunidades-de-trabalho/)\n[ Licitações e Contratações ](https://www.sescsp.org.br/licitacoes-e-contratacoes/)\n[ Credencial Plena ](https://portal.sescsp.org.br/servicos/1_CREDENCIAL+PLENA#/content=59credencialplena)\n[ Política de privacidade ](https://www.sescsp.org.br/politica-de-privacidade/)\n[ Termos de Uso ](https://www.sescsp.org.br/)\n[ Fale Conosco ](https://www.sescsp.org.br/assistente-virtual/)\n![Logo do Sesc](https://www.sescsp.org.br//wp-content/plugins/sesc-menu/src/assets/logo.svg)\n[ Programação ](https://www.sescsp.org.br/programacao)\n[ Editorial ](https://www.sescsp.org.br/editorial/)\n[ Serviços ](https://www.sescsp.org.br/#espacos-servicos)\n[ Central de Relacionamento ](https://centralrelacionamento.sescsp.org.br/)\n[ Loja ](https://portal.sescsp.org.br/loja/#/content=lancamentos/tagcloud=lista)\n[ Mais Sesc ](https://www.sescsp.org.br/programacao/cores-e-caras-mascaras-infantis/)\n![close-button](https://www.sescsp.org.br/wp-content/plugins/sesc-menu/src/assets/close.svg)\n[Home](https://www.sescsp.org.br) |  [Itaquera](https://www.sescsp.org.br/unidades/itaquera) |  [Sem categoria](https://www.sescsp.org.br/categorias-atividades/sem-categoria/) |  Cores e Caras: Máscaras I…\n![Cores e Caras Máscaras Infantis - Foto Alexandre Leal Goes](https://www.sescsp.org.br/wp-content/uploads/2026/06/Cores-e-Caras-Mascaras-Infantis-Foto-Alexandre-Leal-Goes-664x332.png)\nCores e Caras Máscaras Infantis - Foto Alexandre Leal Goes\n## Cores e Caras: Máscaras Infantis\n### Com Equipe do Espaço de Brincar - Ale Goes e Ana Rodrigues\n[ Itaquera ](https://www.sescsp.org.br/unidades/itaquera)\nL\n* [Cursos e Oficinas](https://www.sescsp.org.br/tipos-linguagens/cursos-e-oficinas/)\natividade presencial\nGrátis\nLocal: QUIOSQUE DA PRAÇA\nDatas e horários\n11/07 a 25/07Sábados, às 10h30\n![Cores e Caras Máscaras Infantis - Foto Alexandre Leal Goes](https://www.sescsp.org.br/wp-content/uploads/2026/06/Cores-e-Caras-Mascaras-Infantis-Foto-Alexandre-Leal-Goes-664x332.png)\nCores e Caras Máscaras Infantis - Foto Alexandre Leal Goes\nCompartilhe:\n[ ![ícone facebook](https://www.sescsp.org.br/wp-content/themes/sesc-portal/build/images/new-redes-sociais/facebook.svg) ](https://www.facebook.com/sharer/sharer.php?u=https://www.sescsp.org.br/programacao/cores-e-caras-mascaras-infantis) [ ![ícone whatsapp](https://www.sescsp.org.br/wp-content/themes/sesc-portal/build/images/new-redes-sociais/whats.svg) ](https://wa.me/?text=https://www.sescsp.org.br/programacao/cores-e-caras-mascaras-infantis) [ ![ícone x](https://www.sescsp.org.br/wp-content/themes/sesc-portal/build/images/new-redes-sociais/twitter.svg) ](https://twitter.com/intent/tweet?text=https://www.sescsp.org.br/programacao/cores-e-caras-mascaras-infantis) ![ícone email](https://www.sescsp.org.br/wp-content/themes/sesc-portal/build/images/new-redes-sociais/mail.svg) [ ![ícone pinterest](https://www.sescsp.org.br/wp-content/themes/sesc-portal/build/images/new-redes-sociais/pinterest.svg) ](http://pinterest.com/pin/create/link/?url=https://www.sescsp.org.br/programacao/cores-e-caras-mascaras-infantis)\nA oficina “Caras e Cores: Máscaras InfantiS” convida as crianças a darem uma nova vida a materiais que seriam descartados. Através do recorte (com auxílio), pintura e colagem em papelão, os pequenos e seus responsáveis criam personagens únicos, explorando texturas e relevos naturais do material. É uma jornada que une a alegria criativa ao respeito pela natureza, transformando o simples em mágico.\nFechar\n##### Escolha o evento para adicionar à agenda\n[ 11/07/26 • 10h30 ](http://www.google.com/calendar/render?%0A%09%09%09%09%09%09%09%09action=TEMPLATE%0A%09%09%09%09%09%09%09%09%09&text=Cores+e+Caras%3A+M%C3%A1scaras+Infantis%09%09%09%09%09%09%09%09%09&dates=20260711T103000/20260711T103000%09%09%09%09%09%09%09%09%09&details=A+oficina+%26%238220%3BCaras+e+Cores%3A+M%C3%A1scaras+InfantiS%26%238221%3B+convida+as+crian%C3%A7as+a+darem+uma+nova+vida+a+materiais+que+seriam+descartados.+Atrav%C3%A9s+do+recorte+%28com+aux%C3%ADlio%29%2C+pintura+e+colagem+em+papel%C3%A3o%2C+os+pequenos+e+seus+respons%C3%A1veis+criam+personagens+%C3%BAnicos%2C+explorando+texturas+e+relevos+naturais+do+material.+%C3%89+uma+jornada+que+une+a+alegria+criativa+ao+respeito+%5B%26hellip%3B%5D%0A%0Ahttps%3A%2F%2Fwww.sescsp.org.br%2Fprogramacao%2Fcores-e-caras-mascaras-infantis%2F%09%09%09%09%09%09%09%09%09&location=)",
        "links": "[\"https://www.sescsp.org.br/wp-content/plugins/sesc-menu/src/assets/logo.svg\", \"https://www.sescsp.org.br/wp-content/plugins/sesc-menu/src/assets/new-caret.svg\", \"https://www.sescsp.org.br/wp-content/plugins/sesc-menu/src/assets/close.svg\", \"https://www.sescsp.org.br/wp-content/plugins/sesc-menu/src/assets/sandwich.svg\", \"https://portal.sescsp.org.br/pt/sobre-o-sesc\", \"https://www.sescsp.org.br/oportunidades-de-trabalho\", \"https://www.sescsp.org.br/licitacoes-e-contratacoes\", \"https://portal.sescsp.org.br/servicos/1_CREDENCIAL+PLENA\", \"https://www.sescsp.org.br/politica-de-privacidade\", \"https://www.sescsp.org.br\", \"https://www.sescsp.org.br/assistente-virtual\", \"https://www.sescsp.org.br//wp-content/plugins/sesc-menu/src/assets/logo.svg\"]"
      },
      {
        "level": "1",
        "url": "https://www.sescsp.org.br/programacao/territorio-do-brincar-3",
        "markdown": "[![Logo do Sesc](https://www.sescsp.org.br/wp-content/plugins/sesc-menu/src/assets/logo.svg)](https://www.sescsp.org.br)\nInstitucional![Mini ícone de um triângulo, indicando se a lista de links está aberta ou fechada.](https://www.sescsp.org.br/wp-content/plugins/sesc-menu/src/assets/new-caret.svg)\nUnidades![Mini ícone de um triângulo, indicando se a lista de links está aberta ou fechada.](https://www.sescsp.org.br/wp-content/plugins/sesc-menu/src/assets/new-caret.svg)\n![close-button](https://www.sescsp.org.br/wp-content/plugins/sesc-menu/src/assets/close.svg)\n![Ícone de configurações, com três barras horizontais paralelas, representando o 'menu sanduíche'.](https://www.sescsp.org.br/wp-content/plugins/sesc-menu/src/assets/sandwich.svg)\n[ Sobre o Sesc ](https://portal.sescsp.org.br/pt/sobre-o-sesc/)\n[ Oportunidades de Trabalho ](https://www.sescsp.org.br/oportunidades-de-trabalho/)\n[ Licitações e Contratações ](https://www.sescsp.org.br/licitacoes-e-contratacoes/)\n[ Credencial Plena ](https://portal.sescsp.org.br/servicos/1_CREDENCIAL+PLENA#/content=59credencialplena)\n[ Política de privacidade ](https://www.sescsp.org.br/politica-de-privacidade/)\n[ Termos de Uso ](https://www.sescsp.org.br/)\n[ Fale Conosco ](https://www.sescsp.org.br/assistente-virtual/)\n![Logo do Sesc](https://www.sescsp.org.br//wp-content/plugins/sesc-menu/src/assets/logo.svg)\n[ Programação ](https://www.sescsp.org.br/programacao)\n[ Editorial ](https://www.sescsp.org.br/editorial/)\n[ Serviços ](https://www.sescsp.org.br/#espacos-servicos)\n[ Central de Relacionamento ](https://centralrelacionamento.sescsp.org.br/)\n[ Loja ](https://portal.sescsp.org.br/loja/#/content=lancamentos/tagcloud=lista)\n[ Mais Sesc ](https://www.sescsp.org.br/programacao/territorio-do-brincar-3/)\n![close-button](https://www.sescsp.org.br/wp-content/plugins/sesc-menu/src/assets/close.svg)\n[Home](https://www.sescsp.org.br) |  [14 Bis](https://www.sescsp.org.br/unidades/14-bis) |  [Sem categoria](https://www.sescsp.org.br/categorias-atividades/sem-categoria/) |  Território do Brincar\n![Foto: Reprodução](https://www.sescsp.org.br/wp-content/uploads/2026/06/Midia-13-e1781992835938-664x332.jpg)\nFoto: Reprodução\n## Território do Brincar\n### Com Caê Coragem\n[ 14 Bis ](https://www.sescsp.org.br/unidades/14-bis)\nDuração: **360 minutos**\nL\n* [Esporte e Atividade Física](https://www.sescsp.org.br/tipos-linguagens/esporte-e-atividade-fisica/)\n* [Práticas Corporais](https://www.sescsp.org.br/tipos-linguagens/praticas-corporais/)\natividade presencial\nGrátis\nLocal: Espaço de brincar - Piso térreo\nDatas e horários\n14/07 a 22/07Terças a domingos, às 09h30\n![Foto: Reprodução](https://www.sescsp.org.br/wp-content/uploads/2026/06/Midia-13-e1781992835938-664x332.jpg)\nFoto: Reprodução\nCompartilhe:\n[ ![ícone facebook](https://www.sescsp.org.br/wp-content/themes/sesc-portal/build/images/new-redes-sociais/facebook.svg) ](https://www.facebook.com/sharer/sharer.php?u=https://www.sescsp.org.br/programacao/territorio-do-brincar-3) [ ![ícone whatsapp](https://www.sescsp.org.br/wp-content/themes/sesc-portal/build/images/new-redes-sociais/whats.svg) ](https://wa.me/?text=https://www.sescsp.org.br/programacao/territorio-do-brincar-3) [ ![ícone x](https://www.sescsp.org.br/wp-content/themes/sesc-portal/build/images/new-redes-sociais/twitter.svg) ](https://twitter.com/intent/tweet?text=https://www.sescsp.org.br/programacao/territorio-do-brincar-3) ![ícone email](https://www.sescsp.org.br/wp-content/themes/sesc-portal/build/images/new-redes-sociais/mail.svg) [ ![ícone pinterest](https://www.sescsp.org.br/wp-content/themes/sesc-portal/build/images/new-redes-sociais/pinterest.svg) ](http://pinterest.com/pin/create/link/?url=https://www.sescsp.org.br/programacao/territorio-do-brincar-3)\nNo Território do Brincar, bebês e crianças até 6 anos são convidados a explorar, imaginar e descobrir o mundo por meio de experiências sensoriais, brincadeiras e encontros afetivos. Com mediação acolhedora, o espaço promove vínculos, curiosidade, movimento e criação, valorizando o brincar livre como parte essencial do desenvolvimento infantil.\nO programa Espaço de Brincar oferece um acervo diverso com brinquedos e itens não estruturados que convidam as crianças a explorar possibilidades e imaginação no brincar. A mediação do brincar livre enriquece e diversifica as possibilidades de uso do acervo e de suas relações com as outras crianças e suas pessoas cuidadoras acompanhantes.\nCaê Coragem é arte educador formado em Licenciatura em arte teatro na UNESP e em percussão popular na Emesp.\nAtua como músico, sonoplasta, produtor cultural e tradutor interprete de língua de sinais e português.\nTem contato com a comunidade surda desde 2015 a partir do Slam do Corpo criando poesia em parceria com poetas surdes. Desde então vem pesquisando o encontro da cultura surda com a cultura ouvinte e o encontro das linguas Libras e português nas diferentes esferas da arte.\nComo arte educador com foco nas linguagens música e teatro ja atuou no programa PIÁ na casa de Cultura Chico Science, no Centro Cultural Kalunguinha, no coletivo Sentindo os Sentidos entre diversos outros espaços, instituições e coletividades autônomas.",
        "links": "[\"https://www.sescsp.org.br/wp-content/plugins/sesc-menu/src/assets/logo.svg\", \"https://www.sescsp.org.br/wp-content/plugins/sesc-menu/src/assets/new-caret.svg\", \"https://www.sescsp.org.br/wp-content/plugins/sesc-menu/src/assets/close.svg\", \"https://www.sescsp.org.br/wp-content/plugins/sesc-menu/src/assets/sandwich.svg\", \"https://portal.sescsp.org.br/pt/sobre-o-sesc\", \"https://www.sescsp.org.br/oportunidades-de-trabalho\", \"https://www.sescsp.org.br/licitacoes-e-contratacoes\", \"https://portal.sescsp.org.br/servicos/1_CREDENCIAL+PLENA\", \"https://www.sescsp.org.br/politica-de-privacidade\", \"https://www.sescsp.org.br\", \"https://www.sescsp.org.br/assistente-virtual\", \"https://www.sescsp.org.br//wp-content/plugins/sesc-menu/src/assets/logo.svg\"]"
      },
      {
        "level": "1",
        "url": "https://www.sescsp.org.br/programacao/do-piao-a-pipa-brincadeiras-de-rua-projeto-de-ferias-sesc-belenzinho",
        "markdown": "[![Logo do Sesc](https://www.sescsp.org.br/wp-content/plugins/sesc-menu/src/assets/logo.svg)](https://www.sescsp.org.br)\nInstitucional![Mini ícone de um triângulo, indicando se a lista de links está aberta ou fechada.](https://www.sescsp.org.br/wp-content/plugins/sesc-menu/src/assets/new-caret.svg)\nUnidades![Mini ícone de um triângulo, indicando se a lista de links está aberta ou fechada.](https://www.sescsp.org.br/wp-content/plugins/sesc-menu/src/assets/new-caret.svg)\n![close-button](https://www.sescsp.org.br/wp-content/plugins/sesc-menu/src/assets/close.svg)\n![Ícone de configurações, com três barras horizontais paralelas, representando o 'menu sanduíche'.](https://www.sescsp.org.br/wp-content/plugins/sesc-menu/src/assets/sandwich.svg)\n[ Sobre o Sesc ](https://portal.sescsp.org.br/pt/sobre-o-sesc/)\n[ Oportunidades de Trabalho ](https://www.sescsp.org.br/oportunidades-de-trabalho/)\n[ Licitações e Contratações ](https://www.sescsp.org.br/licitacoes-e-contratacoes/)\n[ Credencial Plena ](https://portal.sescsp.org.br/servicos/1_CREDENCIAL+PLENA#/content=59credencialplena)\n[ Política de privacidade ](https://www.sescsp.org.br/politica-de-privacidade/)\n[ Termos de Uso ](https://www.sescsp.org.br/)\n[ Fale Conosco ](https://www.sescsp.org.br/assistente-virtual/)\n![Logo do Sesc](https://www.sescsp.org.br//wp-content/plugins/sesc-menu/src/assets/logo.svg)\n[ Programação ](https://www.sescsp.org.br/programacao)\n[ Editorial ](https://www.sescsp.org.br/editorial/)\n[ Serviços ](https://www.sescsp.org.br/#espacos-servicos)\n[ Central de Relacionamento ](https://centralrelacionamento.sescsp.org.br/)\n[ Loja ](https://portal.sescsp.org.br/loja/#/content=lancamentos/tagcloud=lista)\n[ Mais Sesc ](https://www.sescsp.org.br/programacao/do-piao-a-pipa-brincadeiras-de-rua-projeto-de-ferias-sesc-belenzinho/)\n![close-button](https://www.sescsp.org.br/wp-content/plugins/sesc-menu/src/assets/close.svg)\n[Home](https://www.sescsp.org.br) |  [Belenzinho](https://www.sescsp.org.br/unidades/belenzinho) |  [Sem categoria](https://www.sescsp.org.br/categorias-atividades/sem-categoria/) |  “Do Pião à Pipa: Br…\n![Foto: Gerada por IA](https://www.sescsp.org.br/wp-content/uploads/2026/06/ChatGPT-Image-26-de-jun.-de-2026-14_35_14-664x332.png)\nFoto: Gerada por IA\n## “Do Pião à Pipa: Brincadeiras de Rua” – Projeto de Férias Sesc Belenzinho\n[ Belenzinho ](https://www.sescsp.org.br/unidades/belenzinho)\nDuração: **210 minutos**\n* [Esporte e Atividade Física](https://www.sescsp.org.br/tipos-linguagens/esporte-e-atividade-fisica/)\n* [Programa Sesc de Esportes](https://www.sescsp.org.br/tipos-linguagens/programa-sesc-de-esportes/)\natividade presencial\nGrátis\nLocal: Ponto de Encontro - Ginásio Sesc Belenzinho\nDatas e horários\n[Inscrever](https://centralrelacionamento.sescsp.org.br/)\n14/07 a 17/07Terças a sextas, às 14h00\n![Foto: Gerada por IA](https://www.sescsp.org.br/wp-content/uploads/2026/06/ChatGPT-Image-26-de-jun.-de-2026-14_35_14-664x332.png)\nFoto: Gerada por IA\nCompartilhe:\n[ ![ícone facebook](https://www.sescsp.org.br/wp-content/themes/sesc-portal/build/images/new-redes-sociais/facebook.svg) ](https://www.facebook.com/sharer/sharer.php?u=https://www.sescsp.org.br/programacao/do-piao-a-pipa-brincadeiras-de-rua-projeto-de-ferias-sesc-belenzinho) [ ![ícone whatsapp](https://www.sescsp.org.br/wp-content/themes/sesc-portal/build/images/new-redes-sociais/whats.svg) ](https://wa.me/?text=https://www.sescsp.org.br/programacao/do-piao-a-pipa-brincadeiras-de-rua-projeto-de-ferias-sesc-belenzinho) [ ![ícone x](https://www.sescsp.org.br/wp-content/themes/sesc-portal/build/images/new-redes-sociais/twitter.svg) ](https://twitter.com/intent/tweet?text=https://www.sescsp.org.br/programacao/do-piao-a-pipa-brincadeiras-de-rua-projeto-de-ferias-sesc-belenzinho) ![ícone email](https://www.sescsp.org.br/wp-content/themes/sesc-portal/build/images/new-redes-sociais/mail.svg) [ ![ícone pinterest](https://www.sescsp.org.br/wp-content/themes/sesc-portal/build/images/new-redes-sociais/pinterest.svg) ](http://pinterest.com/pin/create/link/?url=https://www.sescsp.org.br/programacao/do-piao-a-pipa-brincadeiras-de-rua-projeto-de-ferias-sesc-belenzinho)\nEm julho, mês de férias, o Sesc Belenzinho oferece o projeto “Do pião à pipa: brincadeiras de rua”, uma programação especial que resgatará jogos e atividades tradicionais presentes na cultura das ruas brasileiras.\nEm uma semana de vivências lúdicas, as crianças serão convidadas a descobrir, explorar e experimentar brinquedos que marcaram gerações como o pião, a pipa, o jogo de taco e o carrinho de rolimã valorizando o movimento, a criatividade e a convivência.\nEntre construções manuais, jogos ao ar livre e desafios que envolvem corpo e criatividade, cada criança terá a oportunidade de brincar e compartilhar memórias afetivas que atravessam o tempo e celebram a essência do brincar livre.\nPara encerrar a semana, teremos uma saída para o Museu do Ipiranga onde as crianças experimentarão uma descida de carrinho de rolimã em um dos pontos mais famosos da cidade de São Paulo. (Programação sujeita a alterações em função das condições climáticas).",
        "links": "[\"https://www.sescsp.org.br/wp-content/plugins/sesc-menu/src/assets/logo.svg\", \"https://www.sescsp.org.br/wp-content/plugins/sesc-menu/src/assets/new-caret.svg\", \"https://www.sescsp.org.br/wp-content/plugins/sesc-menu/src/assets/close.svg\", \"https://www.sescsp.org.br/wp-content/plugins/sesc-menu/src/assets/sandwich.svg\", \"https://portal.sescsp.org.br/pt/sobre-o-sesc\", \"https://www.sescsp.org.br/oportunidades-de-trabalho\", \"https://www.sescsp.org.br/licitacoes-e-contratacoes\", \"https://portal.sescsp.org.br/servicos/1_CREDENCIAL+PLENA\", \"https://www.sescsp.org.br/politica-de-privacidade\", \"https://www.sescsp.org.br\", \"https://www.sescsp.org.br/assistente-virtual\", \"https://www.sescsp.org.br//wp-content/plugins/sesc-menu/src/assets/logo.svg\"]"
      },
      {
        "level": "1",
        "url": "https://saopauloparacriancas.com.br",
        "markdown": "[ ](javascript:void\\(0\\))\n[ ![](https://saopauloparacriancas.com.br/wp-content/themes/sppc2025/images/menu.svg) ](javascript:void\\(0\\)) [ ![](https://saopauloparacriancas.com.br/wp-content/themes/sppc2025/images/logo-sppc.svg) ](https://saopauloparacriancas.com.br)\n[Home](https://saopauloparacriancas.com.br) [O que fazer](https://saopauloparacriancas.com.br/passeios/) [Onde comer](https://saopauloparacriancas.com.br/passeios/onde-comer/) [Viajar](https://saopauloparacriancas.com.br/viajar/) [Últimas notícias](https://saopauloparacriancas.com.br/ultimas-noticias/) [Compras](https://saopauloparacriancas.com.br/compras/) [Descontos](https://saopauloparacriancas.com.br/descontos/) [Sobre nós](https://saopauloparacriancas.com.br/quem-somos/) [ ![](https://saopauloparacriancas.com.br/wp-content/themes/sppc2025/images/fecha.svg) ](javascript:void\\(0\\)) [ ![](https://saopauloparacriancas.com.br/wp-content/themes/sppc2025/images/Grupo-211.svg) Login ](https://saopauloparacriancas.com.br/login/)\n[ ![](https://saopauloparacriancas.com.br/wp-content/themes/sppc2025/images/Grupo-211.svg) ](https://saopauloparacriancas.com.br/) [ ![](https://saopauloparacriancas.com.br/wp-content/themes/sppc2025/images/lupa.svg) ](https://saopauloparacriancas.com.br/)\nIndicações\n[ ![](https://saopauloparacriancas.com.br/wp-content/themes/sppc2025/images/icone-bt-ir.svg) ](https://saopauloparacriancas.com.br/passeios)\n[ ![](https://saopauloparacriancas.com.br/wp-content/uploads/2026/07/Programacao-de-feris-pullman-guarulhos-800x534.jpg) 05/07, 09/07, 11/07, 18/07, 19/07, 26/07 Férias de julho no Pullman Guarulhos hotel terá teatro, Chá da Alice e atrações para crianças a partir de R$15 ](https://saopauloparacriancas.com.br/pullman-guarulhos/)\n[ ![](https://saopauloparacriancas.com.br/wp-content/uploads/2026/06/passeios-gratuitos-ferias-sp-800x534.jpg) Atração fixa 31 passeios gratuitos para fazer com crianças nas férias de julho em São Paulo (2026) ](https://saopauloparacriancas.com.br/passeios-gratuitos-ferias/)\n[ ![](https://saopauloparacriancas.com.br/wp-content/uploads/2026/06/ferias-pinacoteca-800x534.jpg) Atração fixa Pinacoteca de São Paulo tem programação gratuita para crianças durante as férias de julho ](https://saopauloparacriancas.com.br/pinacoteca-sp/)\n[ ![](https://saopauloparacriancas.com.br/wp-content/uploads/2026/06/Casa-de-cultura-do-parque-800x534.jpg) 04/07 a 31/07 Férias de julho em SP Casa de Cultura do Parque tem oficinas gratuitas para crianças durante todo o mês ](https://saopauloparacriancas.com.br/casa-de-cultura-do-parque-2/)\n[ ![](https://saopauloparacriancas.com.br/wp-content/uploads/2026/06/Water-Lantern-Festival-S.png) 11/07 a 12/07 Festival de Lanternas inédito chega a São Paulo nas férias de Julho! ](https://saopauloparacriancas.com.br/water-lantern-festival/)\n[ ![](https://saopauloparacriancas.com.br/wp-content/uploads/2026/05/festa-do-morango-atibaia-e-jarinu.png) 05/07, 11/07, 12/07, 18/07, 19/07 Festa do Morango 2026 em Atibaia e Jarinu terá entrada grátis e programação para famílias ](https://saopauloparacriancas.com.br/festa-do-morango-atibaia-e-jarinu/)\n[ ![](https://saopauloparacriancas.com.br/wp-content/uploads/2026/05/unnamed.jpg) 16/05 a 09/08 Guarulhos recebe kart com realidade virtual inspirado em games no Internacional Shopping ](https://saopauloparacriancas.com.br/kart-virtual-internacional-guarulhos/)\n[ ![](https://saopauloparacriancas.com.br/wp-content/uploads/2026/05/spcriancas_passeios_kidzhouse.png) 24/07 a 26/07 Kidzhouse Festival 2026 anuncia Enaldinho, Kysha e Mine, Mussa e mais atrações em São Paulo ](https://saopauloparacriancas.com.br/kidzhouse-festival-2026/)\n[ ![](https://saopauloparacriancas.com.br/wp-content/uploads/2026/04/sp_criancas_rolex_6h_de_sao_paulo_2026_4.jpg) 10/07, 11/07, 12/07 Rolex 6 Horas de São Paulo festival para amantes do automobilismo acontece em julho ](https://saopauloparacriancas.com.br/rolex-6h-de-sao-paulo-festival-automobilismo-2026/)\n[ ![](https://saopauloparacriancas.com.br/wp-content/uploads/2026/04/sp_criancas_henry_e_klaus_masters_of_magic_1.jpg) 30/05 a 02/08 Henry & Klauss apresentam novo show em São Paulo Masters of Magic ](https://saopauloparacriancas.com.br/henry-klauss-masters-of-magic/)\n[ ![](https://saopauloparacriancas.com.br/wp-content/uploads/2026/03/sp_criancas_passseio_disney_06-800x533.jpeg) 24/06 a 05/07 Disney On Ice em São Paulo com desconto Frozen, Encanto e participação inédita de Stitch ](https://saopauloparacriancas.com.br/disney-on-ice-2026/)\n[ ![](https://saopauloparacriancas.com.br/wp-content/uploads/2025/11/sp_criancas_jucabowling_maio2026_2.jpg) Atração fixa O que fazer com crianças em São Paulo? Parque de trampolins e boliche são atrações do JucaBowling ](https://saopauloparacriancas.com.br/boliche-trampolim-festas-jucabowling-sp/)\n[ ![](https://saopauloparacriancas.com.br/wp-content/uploads/2025/07/glow-park.png) Atração fixa Arraiá no Glow Park crianças com trajes caipiras ganham 10% de desconto ](https://saopauloparacriancas.com.br/glow-park-2025/)",
        "links": "[\"https://saopauloparacriancas.com.br/wp-content/themes/sppc2025/images/menu.svg\", \"https://saopauloparacriancas.com.br/wp-content/themes/sppc2025/images/logo-sppc.svg\", \"https://saopauloparacriancas.com.br\", \"https://saopauloparacriancas.com.br/passeios\", \"https://saopauloparacriancas.com.br/passeios/onde-comer\", \"https://saopauloparacriancas.com.br/viajar\", \"https://saopauloparacriancas.com.br/ultimas-noticias\", \"https://saopauloparacriancas.com.br/compras\", \"https://saopauloparacriancas.com.br/descontos\", \"https://saopauloparacriancas.com.br/quem-somos\", \"https://saopauloparacriancas.com.br/wp-content/themes/sppc2025/images/fecha.svg\", \"https://saopauloparacriancas.com.br/wp-content/themes/sppc2025/images/Grupo-211.svg\"]"
      },
      {
        "level": "1",
        "url": "https://capital.sp.gov.br/web/cultura/w/patrimonio_historico/jornada_do_patrimonio/programacao/35790",
        "markdown": "[ Pular para o Conteúdo principal ](https://prefeitura.sp.gov.br/web/cultura/w/patrimonio_historico/jornada_do_patrimonio/programacao/35790#main-content)\n_warning_\nErro\n## Página não encontrada\nNão encontramos a página que você tentou acessar\n[Continue navegando](https://prefeitura.sp.gov.br/)\n**A Prefeitura de São Paulo valoriza sua privacidade!**\nEm nosso site, utilizamos cookies, que são arquivos salvos no seu computador para auxiliar a coletar informações sobre suas preferências e sobre outras páginas da internet visitadas por você a fim de otimizar sua experiência de navegação em nosso site, apresentando conteúdos personalizados. Ao selecionar \"Aceitar todos\", você consente com a utilização de cookies. [Saiba mais](https://capital.sp.gov.br/web/controladoria_geral/w/coordenadoria_de_protecao_de_dados_pessoais/w/encarregado-pelo-tratamento-de-dados-pessoais)\nConfiguração\nAceitar tudo\nRecusar tudo",
        "links": "[\"https://prefeitura.sp.gov.br/web/cultura/w/patrimonio_historico/jornada_do_patrimonio/programacao/35790\", \"https://prefeitura.sp.gov.br\", \"https://capital.sp.gov.br/web/controladoria_geral/w/coordenadoria_de_protecao_de_dados_pessoais/w/encarregado-pelo-tratamento-de-dados-pessoais\"]"
      },
      {
        "level": "1",
        "url": "https://www.sescsp.org.br/ja-tem-programacao-para-este-fim-de-semana-vem-pro-sesc-avenida-paulista/?buscar_curso=0&palavra&unidade_id=2&ATIVIDADE_ID=0&data2=0",
        "markdown": "[![Logo do Sesc](https://www.sescsp.org.br/wp-content/plugins/sesc-menu/src/assets/logo.svg)](https://www.sescsp.org.br)\nInstitucional![Mini ícone de um triângulo, indicando se a lista de links está aberta ou fechada.](https://www.sescsp.org.br/wp-content/plugins/sesc-menu/src/assets/new-caret.svg)\nUnidades![Mini ícone de um triângulo, indicando se a lista de links está aberta ou fechada.](https://www.sescsp.org.br/wp-content/plugins/sesc-menu/src/assets/new-caret.svg)\n![close-button](https://www.sescsp.org.br/wp-content/plugins/sesc-menu/src/assets/close.svg)\n![Ícone de configurações, com três barras horizontais paralelas, representando o 'menu sanduíche'.](https://www.sescsp.org.br/wp-content/plugins/sesc-menu/src/assets/sandwich.svg)\n[ Sobre o Sesc ](https://portal.sescsp.org.br/pt/sobre-o-sesc/)\n[ Oportunidades de Trabalho ](https://www.sescsp.org.br/oportunidades-de-trabalho/)\n[ Licitações e Contratações ](https://www.sescsp.org.br/licitacoes-e-contratacoes/)\n[ Credencial Plena ](https://portal.sescsp.org.br/servicos/1_CREDENCIAL+PLENA#/content=59credencialplena)\n[ Política de privacidade ](https://www.sescsp.org.br/politica-de-privacidade/)\n[ Termos de Uso ](https://www.sescsp.org.br/)\n[ Fale Conosco ](https://www.sescsp.org.br/assistente-virtual/)\n![Logo do Sesc](https://www.sescsp.org.br//wp-content/plugins/sesc-menu/src/assets/logo.svg)\n[ Programação ](https://www.sescsp.org.br/programacao)\n[ Editorial ](https://www.sescsp.org.br/editorial/)\n[ Serviços ](https://www.sescsp.org.br/#espacos-servicos)\n[ Central de Relacionamento ](https://centralrelacionamento.sescsp.org.br/)\n[ Loja ](https://portal.sescsp.org.br/loja/#/content=lancamentos/tagcloud=lista)\n[ Mais Sesc ](https://www.sescsp.org.br/ja-tem-programacao-para-este-fim-de-semana-vem-pro-sesc-avenida-paulista/?buscar_curso=0&palavra&unidade_id=2&ATIVIDADE_ID=0&data2=0)\n![close-button](https://www.sescsp.org.br/wp-content/plugins/sesc-menu/src/assets/close.svg)\n[Home](https://www.sescsp.org.br) |  [Avenida Paulista](https://www.sescsp.org.br/unidades/avenida-paulista) | [Editorial](https://www.sescsp.org.br) |  [Unidades](https://www.sescsp.org.br/category/unidades/) |  Já tem programação para e…\n##  Já tem programação para este fim de semana? Vem pro Sesc Avenida Paulista!\n14/07/2023\nCompartilhe:\n[ ![ícone facebook](https://www.sescsp.org.br/wp-content/themes/sesc-portal/build/images/new-redes-sociais/facebook.svg) ](https://www.facebook.com/sharer/sharer.php?u=https://www.sescsp.org.br/ja-tem-programacao-para-este-fim-de-semana-vem-pro-sesc-avenida-paulista) [ ![ícone whatsapp](https://www.sescsp.org.br/wp-content/themes/sesc-portal/build/images/new-redes-sociais/whats.svg) ](https://wa.me/?text=https://www.sescsp.org.br/ja-tem-programacao-para-este-fim-de-semana-vem-pro-sesc-avenida-paulista) [ ![ícone x](https://www.sescsp.org.br/wp-content/themes/sesc-portal/build/images/new-redes-sociais/twitter.svg) ](https://twitter.com/intent/tweet?text=https://www.sescsp.org.br/ja-tem-programacao-para-este-fim-de-semana-vem-pro-sesc-avenida-paulista) ![ícone email](https://www.sescsp.org.br/wp-content/themes/sesc-portal/build/images/new-redes-sociais/mail.svg) [ ![ícone pinterest](https://www.sescsp.org.br/wp-content/themes/sesc-portal/build/images/new-redes-sociais/pinterest.svg) ](http://pinterest.com/pin/create/link/?url=https://www.sescsp.org.br/ja-tem-programacao-para-este-fim-de-semana-vem-pro-sesc-avenida-paulista)\n![](https://www.sescsp.org.br/wp-content/uploads/2023/07/bonecobumba-meu-boi.jpg)\nBoneco Enfeitado de Bumba-meu-boi. Foto: Léo Britto\n## FestA! – Festival de Aprender\n**15/7, sábado**\n10h30 e 14h – [Chapéus do Palhaço Mateus](https://www.sescsp.org.br/programacao/chapeus-do-palhaco-mateus/) (térreo)\n10h30 e 14h – [Boneco Enfeitado de Bumba-meu-boi](https://www.sescsp.org.br/programacao/boneco-enfeitado-de-bumba-meu-boi/) (térreo)\n11h e 14h30 – [Dança e Inteligência Artificial](https://www.sescsp.org.br/programacao/danca-e-inteligencia-artificial/) (4º andar)*\n**16/7, domingo**\n10h30 e 14h – [Chapéus do Palhaço Mateus](https://www.sescsp.org.br/programacao/chapeus-do-palhaco-mateus/) (térreo)\n10h30 e 14h – [Boneco Enfeitado de Bumba-meu-boi](https://www.sescsp.org.br/programacao/boneco-enfeitado-de-bumba-meu-boi/) (térreo)\n10h30 e 14h – [A arte em miriti como símbolo da cultura popular paraense](https://www.sescsp.org.br/programacao/a-arte-em-miriti-como-simbolo-da-cultura-popular-paraense/) (térreo)\n11h e 14h30 – [Dança e Inteligência Artificial](https://www.sescsp.org.br/programacao/danca-e-inteligencia-artificial/) (4º andar)*\n_* Vagas limitadas. Inscrições no local._\n![](https://www.sescsp.org.br/wp-content/uploads/2023/06/festadasflores-664x332.jpg)Festa das Flores. Foto: Caio Oviedo\n## Artes Visuais\n**15/7, sábado**\n10h – [alterações vividas absolutamente fantasiosas](https://www.sescsp.org.br/programacao/alteracoes-vividas-absolutamente-fantasiosas/) (5º andar)\n10h – [Evidências Reprimidas](https://www.sescsp.org.br/programacao/evidencias-reprimidas/) (4º andar)",
        "links": "[\"https://www.sescsp.org.br/wp-content/plugins/sesc-menu/src/assets/logo.svg\", \"https://www.sescsp.org.br/wp-content/plugins/sesc-menu/src/assets/new-caret.svg\", \"https://www.sescsp.org.br/wp-content/plugins/sesc-menu/src/assets/close.svg\", \"https://www.sescsp.org.br/wp-content/plugins/sesc-menu/src/assets/sandwich.svg\", \"https://portal.sescsp.org.br/pt/sobre-o-sesc\", \"https://www.sescsp.org.br/oportunidades-de-trabalho\", \"https://www.sescsp.org.br/licitacoes-e-contratacoes\", \"https://portal.sescsp.org.br/servicos/1_CREDENCIAL+PLENA\", \"https://www.sescsp.org.br/politica-de-privacidade\", \"https://www.sescsp.org.br\", \"https://www.sescsp.org.br/assistente-virtual\", \"https://www.sescsp.org.br//wp-content/plugins/sesc-menu/src/assets/logo.svg\"]"
      }
    ],
    "second_level": [
      {
        "level": "2",
        "url": "https://prefeitura.sp.gov.br/web/cultura/w/patrimonio_historico/jornada_do_patrimonio/programacao/35790",
        "markdown": "[ Pular para o Conteúdo principal ](https://prefeitura.sp.gov.br/web/cultura/w/patrimonio_historico/jornada_do_patrimonio/programacao/35790#main-content)\n_warning_\nErro\n## Página não encontrada\nNão encontramos a página que você tentou acessar\n[Continue navegando](https://prefeitura.sp.gov.br/)\n**A Prefeitura de São Paulo valoriza sua privacidade!**\nEm nosso site, utilizamos cookies, que são arquivos salvos no seu computador para auxiliar a coletar informações sobre suas preferências e sobre outras páginas da internet visitadas por você a fim de otimizar sua experiência de navegação em nosso site, apresentando conteúdos personalizados. Ao selecionar \"Aceitar todos\", você consente com a utilização de cookies. [Saiba mais](https://capital.sp.gov.br/web/controladoria_geral/w/coordenadoria_de_protecao_de_dados_pessoais/w/encarregado-pelo-tratamento-de-dados-pessoais)\nConfiguração\nAceitar tudo\nRecusar tudo",
        "links": "[\"https://prefeitura.sp.gov.br/web/cultura/w/patrimonio_historico/jornada_do_patrimonio/programacao/35790\", \"https://prefeitura.sp.gov.br\", \"https://capital.sp.gov.br/web/controladoria_geral/w/coordenadoria_de_protecao_de_dados_pessoais/w/encarregado-pelo-tratamento-de-dados-pessoais\"]"
      }
    ]
  },
  "source_counts": {
    "queries": 7,
    "search_results": 41,
    "first_level_crawled": 6,
    "second_level_crawled": 1
  },
  "tool_providers": [
    "ellements.standard_tools.web.search",
    "ellements.standard_tools.web.crawler"
  ]
}
```

## Final output

# 1. Monitor snapshot

**Conclusion:** Context is **limited**. There is one strong, low-cost, age-appropriate official event inside the next 7 days, plus several promising July vacation activities from a family-events roundup that require verification before acting.

- **Topic:** Things to do with my 6 y.o. child
- **Child age:** 6
- **Mode:** Events
- **Cadence:** Weekly
- **Lookback window:** Next 7 days from run date — interpreted as **05/07/2026 to 12/07/2026**
- **Region:** São Paulo, Brazil, with a few nearby-region items flagged separately
- **Run date:** 05/07/2026
- **Research status:** Deep-intent search was run, but primary-page coverage was uneven.
- **Context status:** **Limited**
  - Strong official SESC pages were crawled.
  - The São Paulo Para Crianças homepage was crawled and surfaced several current July listings, but most individual article pages were **not** crawled.
  - Municipal culture source produced a **404 / página não encontrada**.
  - News/cancellation search failed and fell back to web search with low-signal results.
  - No weather forecast source was injected.
- **Evidence grade:** **Adequate for a bounded shortlist; weak for full weekly coverage**
- **Main gap:** Missing crawls of individual São Paulo Para Crianças event pages and official booking/venue pages for non-SESC items.
- **Decision impact:** Parent can confidently act on the SESC official item; for other items, **verify details before booking or traveling**.

---

# 2. Top findings

## 1. Best low-cost official pick: “Cores e Caras: Máscaras Infantis” — Sesc Itaquera

**Recommendation:** Prioritize this if Itaquera is convenient. It is free, official, child-focused, and inside the next 7 days.

- **What is happening:** Children and caregivers create masks from reused cardboard using cutting with help, painting, and collage.
- **Why it matters for a 6-year-old:** The activity is explicitly infantil, hands-on, creative, and includes adult assistance for cutting. It supports fine motor skills, imagination, and environmental awareness.
- **Source link:** Official SESC page — https://www.sescsp.org.br/programacao/cores-e-caras-mascaras-infantis
  - **Source type / provenance:** Official event page, first-level crawl.
- **Date and time:** **11/07/2026, Saturday, 10h30**. Page lists broader run **11/07 a 25/07, sábados, às 10h30**.
- **Location:** **Sesc Itaquera**, local: **QUIOSQUE DA PRAÇA**.
- **Cost:** **Grátis**.
- **Booking / attendance step:** The crawled page did **not** show an “Inscrever” button. Treat as likely open/free, but verify capacity and whether arrival order applies before going.
- **Age-fit notes:** Page marks classification **“L”** and describes “crianças” with “pequenos e seus responsáveis.” Suitable for a 6-year-old with caregiver supervision.
- **Weather caveat:** Local is “Quiosque da Praça,” which may be outdoor or semi-outdoor. No weather forecast was available in the runtime evidence. Check rain/cold before leaving.
- **Safety / practicality:** Bring a caregiver; expect scissors/recorte with assistance. Good fit for a low-cost outing.
- **Confidence:** **High** for date, time, location, and cost; **medium** for access method because capacity/booking details were not explicit.
- **Strongest caveat:** Distance to Sesc Itaquera may be significant depending on where you live; weather may affect comfort.
- **Practical next step:** Open the SESC page on Friday or Saturday morning and confirm whether the activity is first-come, first-served and whether the unit has any capacity notice.

---

## 2. Promising but needs verification: Férias de julho at Casa de Cultura do Parque — free children’s workshops

**Recommendation:** Worth checking because it appears free and runs throughout July, but do not rely on the homepage teaser alone.

- **What is happening:** São Paulo Para Crianças lists: **“Férias de julho em SP Casa de Cultura do Parque tem oficinas gratuitas para crianças durante todo o mês.”**
- **Why it matters for a 6-year-old:** Free vacation workshops are likely age-appropriate family activities, but the exact age range and workshop formats were not available in the crawled evidence.
- **Source link:** São Paulo Para Crianças homepage — https://saopauloparacriancas.com.br
  - Specific listing visible on homepage: https://saopauloparacriancas.com.br/casa-de-cultura-do-parque-2/
  - **Source type / provenance:** Local family-events roundup homepage, first-level crawl; individual event page not crawled.
- **Date and time:** Homepage says **04/07 a 31/07**. Exact session dates/times were not available in the crawled evidence.
- **Location:** **Casa de Cultura do Parque**. Exact address not available in the crawled evidence.
- **Cost:** Homepage says **oficinas gratuitas**.
- **Booking / attendance step:** Unknown from available crawl. Likely requires checking the individual article or venue page for registration/capacity.
- **Age-fit notes:** “Para crianças” is stated, but age range was not visible. Verify whether 6-year-olds are included.
- **Weather caveat:** Unknown whether activities are indoor or outdoor.
- **Confidence:** **Medium-low**. The listing is current and relevant, but details are incomplete.
- **Strongest caveat:** No official venue page or individual article crawl was available, so schedule and booking are unverified.
- **Practical next step:** Crawl/open the specific São Paulo Para Crianças article and then confirm on Casa de Cultura do Parque’s official channels before going.

---

## 3. Promising free museum option: Pinacoteca de São Paulo July children’s programming

**Recommendation:** Good candidate for a safe, cultural, not-too-expensive outing, but verify exact dates and booking.

- **What is happening:** São Paulo Para Crianças lists: **“Pinacoteca de São Paulo tem programação gratuita para crianças durante as férias de julho.”**
- **Why it matters for a 6-year-old:** Museum vacation programming can be a strong fit for a 6-year-old if activities are interactive, short, and family-oriented.
- **Source link:** São Paulo Para Crianças homepage — https://saopauloparacriancas.com.br
  - Specific listing visible on homepage: https://saopauloparacriancas.com.br/pinacoteca-sp/
  - **Source type / provenance:** Local family-events roundup homepage, first-level crawl; individual article and official Pinacoteca page not crawled.
- **Date and time:** Listed as **“Atração fixa”** with July vacation programming; exact session dates/times not available in the crawled evidence.
- **Location:** **Pinacoteca de São Paulo**. Exact building/session location not available in the crawled evidence.
- **Cost:** Homepage says **programação gratuita**.
- **Booking / attendance step:** Unknown from available crawl. Museum activities may require advance sign-up or have limited capacity.
- **Age-fit notes:** “Para crianças” is stated, but no exact age range was visible.
- **Weather caveat:** Likely largely indoor, but this was not confirmed in the crawled evidence.
- **Confidence:** **Medium-low**.
- **Strongest caveat:** No official Pinacoteca page was crawled, so dates, capacity, and age range are uncertain.
- **Practical next step:** Check the São Paulo Para Crianças article, then verify directly on the Pinacoteca official agenda before promising it to your child.

---

## 4. Low-cost nearby option if Guarulhos is convenient: Férias de julho at Pullman Guarulhos

**Recommendation:** Consider only if Guarulhos is practical for you and you can verify session details. It may be affordable, but hotel-based events can vary in cost and access rules.

- **What is happening:** São Paulo Para Crianças lists: **“Férias de julho no Pullman Guarulhos hotel terá teatro, Chá da Alice e atrações para crianças a partir de R$15.”**
- **Why it matters for a 6-year-old:** Theater and themed children’s activities can fit a 6-year-old well, especially during school vacation.
- **Source link:** São Paulo Para Crianças homepage — https://saopauloparacriancas.com.br
  - Specific listing visible on homepage: https://saopauloparacriancas.com.br/pullman-guarulhos/
  - **Source type / provenance:** Local family-events roundup homepage, first-level crawl; individual article and hotel page not crawled.
- **Date and time:** Homepage lists **05/07, 09/07, 11/07, 18/07, 19/07, 26/07**. Inside this monitor window: **05/07, 09/07, 11/07**.
- **Location:** **Pullman Guarulhos** hotel, Guarulhos. Exact address not available in the crawled evidence.
- **Cost:** “A partir de **R$15**” according to homepage teaser.
- **Booking / attendance step:** Unknown. Hotel events may require advance reservation.
- **Age-fit notes:** Listing says “atrações para crianças,” but exact age range was not visible.
- **Weather caveat:** Likely indoor/hotel-based, but not confirmed.
- **Confidence:** **Medium-low**.
- **Strongest caveat:** Nearby-region, not São Paulo city; exact program, booking, and age range not verified.
- **Practical next step:** Open the specific article and contact the hotel before traveling, especially for the 09/07 or 11/07 sessions.

---

## 5. Higher-caveat novelty option: Water Lantern Festival in São Paulo

**Recommendation:** Interesting but lower priority for a 6-year-old unless you confirm safety, schedule, crowding, nighttime conditions, and cost.

- **What is happening:** São Paulo Para Crianças lists: **“Festival de Lanternas inédito chega a São Paulo nas férias de Julho!”**
- **Why it matters for a 6-year-old:** A lantern festival can be visually engaging, but may involve crowds, evening hours, water proximity, and paid entry.
- **Source link:** São Paulo Para Crianças homepage — https://saopauloparacriancas.com.br
  - Specific listing visible on homepage: https://saopauloparacriancas.com.br/water-lantern-festival/
  - **Source type / provenance:** Local family-events roundup homepage, first-level crawl; individual article and official booking page not crawled.
- **Date and time:** Homepage lists **11/07 a 12/07**.
- **Location:** São Paulo, exact venue not available in the crawled evidence.
- **Cost:** Not available in crawled evidence.
- **Booking / attendance step:** Unknown; likely ticketed, but not verified.
- **Age-fit notes:** No age guidance visible in the crawled evidence.
- **Weather caveat:** Likely outdoor and weather-sensitive, but not confirmed. Check rain, temperature, and event cancellation policy.
- **Confidence:** **Low**.
- **Strongest caveat:** Too many unknowns for a parent to act without opening the event page and official ticketing page.
- **Practical next step:** Verify venue, start/end time, ticket price, child policy, safety around water, and refund/cancellation policy before buying.

---

## 6. Only if your child loves cars/noise: Rolex 6 Horas de São Paulo festival

**Recommendation:** Lower fit for a general 6-year-old outing; consider only for a child already interested in racing and comfortable with crowds/noise.

- **What is happening:** São Paulo Para Crianças lists: **“Rolex 6 Horas de São Paulo festival para amantes do automobilismo acontece em julho.”**
- **Why it matters for a 6-year-old:** Could be exciting for a car-loving child, but noise, crowding, long duration, and cost may reduce age fit.
- **Source link:** São Paulo Para Crianças homepage — https://saopauloparacriancas.com.br
  - Specific listing visible on homepage: https://saopauloparacriancas.com.br/rolex-6h-de-sao-paulo-festival-automobilismo-2026/
  - **Source type / provenance:** Local family-events roundup homepage, first-level crawl; official event page not crawled.
- **Date and time:** Homepage lists **10/07, 11/07, 12/07**.
- **Location:** São Paulo; exact venue not available in crawled evidence.
- **Cost:** Not available.
- **Booking / attendance step:** Unknown.
- **Age-fit notes:** No age range visible. Potential sensory overload for some children.
- **Weather caveat:** Motorsport events may involve outdoor exposure; weather not checked.
- **Confidence:** **Low**.
- **Strongest caveat:** Not clearly “not-too-expensive” or age-gentle; likely requires more planning than a museum/SESC outing.
- **Practical next step:** Verify child ticket policy, ear protection needs, seating/shade, food/water rules, and total cost before considering.

---

## Not ranked for this 7-day window, but important to watch/book ahead

### “Território do Brincar” — Sesc 14 Bis

- **Why not ranked:** Starts **14/07**, outside the 05/07–12/07 window.
- **Source:** Official SESC page — https://www.sescsp.org.br/programacao/territorio-do-brincar-3
- **Key details:** **14/07 a 22/07, terças a domingos, às 09h30**, Sesc **14 Bis**, **Espaço de brincar - Piso térreo**, **grátis**, for **bebês e crianças até 6 anos**, duration **360 minutos**.
- **Parent action:** Excellent fit for a 6-year-old exactly at the upper age limit. Put on next week’s plan and verify access/capacity.

### “Do Pião à Pipa: Brincadeiras de Rua” — Projeto de Férias Sesc Belenzinho

- **Why not ranked:** Starts **14/07**, outside this week’s window, but registration may be relevant now.
- **Source:** Official SESC page — https://www.sescsp.org.br/programacao/do-piao-a-pipa-brincadeiras-de-rua-projeto-de-ferias-sesc-belenzinho
- **Key details:** **14/07 a 17/07, terças a sextas, às 14h00**, Sesc **Belenzinho**, ponto de encontro: **Ginásio Sesc Belenzinho**, **grátis**, page shows **Inscrever** via Central de Relacionamento.
- **Weather caveat:** Official page states programming is **“sujeita a alterações em função das condições climáticas.”**
- **Parent action:** If your child enjoys movement and traditional street games, check registration now.

---

# 3. Source map

## Query families searched

- **Upcoming events:** “programação infantil crianças 6 anos São Paulo próximos 7 dias fim de semana”
- **Official calendars / SESC:** `site:sescsp.org.br/programacao programação infantil crianças São Paulo`
- **Venue calendars:** `site:cataventocultural.org.br programação férias crianças São Paulo`
- **City culture calendar:** `site:capital.sp.gov.br cultura programação infantil crianças São Paulo`
- **Local roundups:** “São Paulo para crianças programação infantil fim de semana férias museu teatro”
- **Age-fit / safety / free activities:** “crianças 6 anos São Paulo gratuito ingresso atividade infantil segura”
- **Cancellations / changes:** “programação infantil São Paulo cancelamento alteração chuva crianças”

## First-level sources crawled

1. **Sesc — Cores e Caras: Máscaras Infantis**
   https://www.sescsp.org.br/programacao/cores-e-caras-mascaras-infantis
   - Strong official event source.
   - Current and inside the window.

2. **Sesc — Território do Brincar**
   https://www.sescsp.org.br/programacao/territorio-do-brincar-3
   - Strong official source.
   - Starts after this monitor window.

3. **Sesc — “Do Pião à Pipa: Brincadeiras de Rua”**
   https://www.sescsp.org.br/programacao/do-piao-a-pipa-brincadeiras-de-rua-projeto-de-ferias-sesc-belenzinho
   - Strong official source.
   - Starts after this monitor window; registration appears relevant.

4. **São Paulo Para Crianças homepage**
   https://saopauloparacriancas.com.br
   - Useful local family-events roundup.
   - Surfaced current July listings.
   - Individual articles were not crawled, limiting confidence.

5. **Prefeitura / Jornada do Patrimônio search result page**
   https://capital.sp.gov.br/web/cultura/w/patrimonio_historico/jornada_do_patrimonio/programacao/35790
   - Crawled result returned **página não encontrada**.

6. **Sesc Avenida Paulista editorial page**
   https://www.sescsp.org.br/ja-tem-programacao-para-este-fim-de-semana-vem-pro-sesc-avenida-paulista/?buscar_curso=0&palavra&unidade_id=2&ATIVIDADE_ID=0&data2=0
   - Rejected as stale: dated **14/07/2023**.

## Second-level sources crawled

- **Prefeitura alternate URL**
  https://prefeitura.sp.gov.br/web/cultura/w/patrimonio_historico/jornada_do_patrimonio/programacao/35790
  - Also returned **página não encontrada**.

## Strongest sources

- Official SESC event pages:
  - https://www.sescsp.org.br/programacao/cores-e-caras-mascaras-infantis
  - https://www.sescsp.org.br/programacao/territorio-do-brincar-3
  - https://www.sescsp.org.br/programacao/do-piao-a-pipa-brincadeiras-de-rua-projeto-de-ferias-sesc-belenzinho

## Useful but weaker sources

- São Paulo Para Crianças homepage:
  - https://saopauloparacriancas.com.br
  - Useful discovery source, but not enough alone for booking, cost, exact schedule, age rules, or safety decisions.

## Rejected or low-signal sources

- **Sesc Avenida Paulista editorial from 2023** — stale for this week.
- **Prefeitura Jornada do Patrimônio page** — inaccessible / not found.
- Search results pointing to unrelated regions, old roundups, ads, generic ticket pages, TikTok, shopping/product pages, or TV schedules were not used for recommendations.

## Gaps

- No official pages crawled for Pinacoteca, Casa de Cultura do Parque, Pullman Guarulhos, Water Lantern Festival, Rolex 6 Horas, Disney On Ice, Festa do Morango, Henry & Klauss, or Glow Park.
- No weather forecast source.
- No live cancellation alerts.
- No transit/distance analysis by neighborhood.
- No systematic crawl of SESC programming filters by date and age.

---

# 4. What changed or what is new

**Conclusion:** No previous-run context was supplied, so change comparison is limited. The items below appear current or newly actionable within the 05/07–12/07 window based on crawled evidence.

- **Appears newly actionable this week:**
  - **Sesc Itaquera — Cores e Caras: Máscaras Infantis**, first occurrence on **11/07**.
  - **Pullman Guarulhos férias programming**, homepage lists dates **05/07, 09/07, 11/07**.
  - **Water Lantern Festival**, homepage lists **11/07 a 12/07**.
  - **Rolex 6 Horas de São Paulo**, homepage lists **10/07, 11/07, 12/07**.
  - **Casa de Cultura do Parque**, listed as **04/07 a 31/07**.
  - **Pinacoteca children’s vacation programming**, listed as a fixed/free July vacation item.

- **Still-important but outside this week:**
  - **Sesc 14 Bis — Território do Brincar**, starts **14/07**.
  - **Sesc Belenzinho — Do Pião à Pipa**, starts **14/07** and may require registration.

- **Comparison limitation:** Without a prior digest, this run cannot identify true additions, removals, sold-out changes, or cancellations compared with last week.

---

# 5. Contradictions, caveats, and missing evidence

## Main caveat: only one high-confidence event inside the window

- The SESC Itaquera mask workshop is the only crawled official event page that is clearly inside the next 7 days, free, and age-appropriate.

## Non-SESC recommendations need verification

- São Paulo Para Crianças provided useful current listings, but homepage teasers do not give enough detail for:
  - exact time;
  - official venue confirmation;
  - ticketing/booking;
  - full price;
  - capacity;
  - exact age range;
  - cancellation/weather policy.

## Weather uncertainty

- No weather forecast was injected.
- SESC Itaquera’s “Quiosque da Praça” may be weather-exposed.
- Water Lantern Festival and motorsport events may be weather-sensitive.
- SESC Belenzinho’s “Do Pião à Pipa,” outside this week, explicitly says programming may change due to weather.

## Age-fit uncertainty

- Strong age-fit:
  - **Território do Brincar** says “bebês e crianças até 6 anos,” but starts after this window.
  - **Cores e Caras** is infantil and classification “L,” but exact age range is not specified.
- Unclear age-fit:
  - Casa de Cultura do Parque;
  - Pinacoteca;
  - Pullman Guarulhos;
  - Water Lantern Festival;
  - Rolex 6 Horas.

## Cost uncertainty

- Confirmed free:
  - SESC Itaquera mask workshop.
  - SESC 14 Bis Território do Brincar, outside window.
  - SESC Belenzinho Do Pião à Pipa, outside window.
- Reported free but not independently verified:
  - Casa de Cultura do Parque workshops.
  - Pinacoteca children’s programming.
- Reported low-cost but not verified:
  - Pullman Guarulhos “a partir de R$15.”
- Unknown or likely paid:
  - Water Lantern Festival.
  - Rolex 6 Horas.
  - Henry & Klauss, Disney On Ice, Glow Park, kart VR, and other commercial attractions listed on the São Paulo Para Crianças homepage.

## Inaccessible / stale sources

- Prefeitura page returned **“Página não encontrada.”**
- SESC Avenida Paulista editorial page was from **2023** and was rejected for this week.

---

# 6. Watchlist for next run

## Queries to monitor

- `site:sescsp.org.br/programacao crianças julho 2026 São Paulo grátis`
- `site:sescsp.org.br/programacao infantil férias julho 2026 Sesc São Paulo`
- `Pinacoteca programação infantil férias julho 2026`
- `Casa de Cultura do Parque oficinas crianças julho 2026`
- `programação infantil fim de semana São Paulo julho 2026`
- `São Paulo para crianças férias julho 2026 gratuito`
- `Museu Catavento programação férias julho 2026 crianças`
- `Bibliotecas municipais São Paulo contação de histórias crianças julho 2026`
- `cancelamento programação infantil São Paulo chuva julho 2026`
- `SESC Belenzinho Do Pião à Pipa inscrições`

## Sources / organizations to monitor

- **SESC São Paulo programação:** https://www.sescsp.org.br/programacao
- **São Paulo Para Crianças:** https://saopauloparacriancas.com.br
- **Pinacoteca de São Paulo**
- **Casa de Cultura do Parque**
- **Catavento Cultural**
- **Museu do Ipiranga**
- **Bibliotecas municipais de São Paulo**
- **Secretaria Municipal de Cultura de São Paulo**
- **SESC units:** Itaquera, Belenzinho, 14 Bis, Avenida Paulista, Pompeia, Pinheiros, Vila Mariana, Consolação
- **Weather/cancellation signals:** official venue Instagram/pages, SESC Central de Relacionamento, ticketing pages

## Specific pages to crawl next

- https://saopauloparacriancas.com.br/casa-de-cultura-do-parque-2/
- https://saopauloparacriancas.com.br/pinacoteca-sp/
- https://saopauloparacriancas.com.br/pullman-guarulhos/
- https://saopauloparacriancas.com.br/water-lantern-festival/
- https://saopauloparacriancas.com.br/rolex-6h-de-sao-paulo-festival-automobilismo-2026/
- https://www.sescsp.org.br/programacao/territorio-do-brincar-3
- https://www.sescsp.org.br/programacao/do-piao-a-pipa-brincadeiras-de-rua-projeto-de-ferias-sesc-belenzinho

---

# 7. Action checklist

## Book / verify now

- **Verify SESC Itaquera “Cores e Caras: Máscaras Infantis”**
  - Confirm whether it is first-come, first-served.
  - Check weather.
  - Plan arrival before **10h30 on 11/07**.
  - Source: https://www.sescsp.org.br/programacao/cores-e-caras-mascaras-infantis

- **Check registration for SESC Belenzinho “Do Pião à Pipa”**
  - Event starts after this window, but official page shows **Inscrever**.
  - Good candidate for next week if spots are available.
  - Source: https://www.sescsp.org.br/programacao/do-piao-a-pipa-brincadeiras-de-rua-projeto-de-ferias-sesc-belenzinho

## Read before promising to your child

- Casa de Cultura do Parque article and official venue page.
- Pinacoteca article and official museum agenda.
- Pullman Guarulhos article and hotel booking/contact details.
- Water Lantern Festival official/ticketing page.
- Rolex 6 Horas official/ticketing page, only if your child is comfortable with loud events.

## Attend

- **Attend SESC Itaquera on 11/07 at 10h30** if location and weather are practical.

## Ignore or deprioritize

- Stale SESC Avenida Paulista 2023 editorial page.
- Prefeitura Jornada do Patrimônio page that returned not found.
- Search results from other cities, ads, generic ticket portals, TikTok, product pages, and old roundups.

## Follow up next run

- Re-check SESC 14 Bis **Território do Brincar** for **14/07–22/07** because it is an excellent age match for a 6-year-old.
- Re-check SESC Belenzinho **Do Pião à Pipa** for availability and weather-sensitive schedule.
- Crawl official pages for Pinacoteca, Casa de Cultura do Parque, and Catavento to improve the next digest.
