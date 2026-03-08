const WORLD_ATLAS_URL = 'https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json';
const NEWS_DATA_URL = './data/news.json';

const svg = d3.select('#map');
const width = 1000;
const height = 520;
const projection = d3.geoNaturalEarth1().scale(175).translate([width / 2, height / 2]);
const path = d3.geoPath(projection);

const regionEl = document.getElementById('selected-region');
const newsListEl = document.getElementById('news-list');
const metaEl = document.getElementById('meta');

const ISO_NUMERIC_TO_ALPHA2 = {
  4: 'AF', 8: 'AL', 12: 'DZ', 32: 'AR', 36: 'AU', 40: 'AT', 50: 'BD', 56: 'BE', 68: 'BO', 76: 'BR',
  100: 'BG', 124: 'CA', 152: 'CL', 156: 'CN', 170: 'CO', 188: 'CR', 191: 'HR', 203: 'CZ', 208: 'DK',
  214: 'DO', 218: 'EC', 818: 'EG', 222: 'SV', 231: 'ET', 246: 'FI', 250: 'FR', 276: 'DE', 300: 'GR',
  320: 'GT', 332: 'HT', 340: 'HN', 344: 'HK', 348: 'HU', 352: 'IS', 356: 'IN', 360: 'ID', 364: 'IR',
  368: 'IQ', 372: 'IE', 376: 'IL', 380: 'IT', 388: 'JM', 392: 'JP', 400: 'JO', 404: 'KE', 410: 'KR',
  414: 'KW', 422: 'LB', 434: 'LY', 458: 'MY', 484: 'MX', 504: 'MA', 528: 'NL', 554: 'NZ', 558: 'NI',
  566: 'NG', 578: 'NO', 586: 'PK', 591: 'PA', 604: 'PE', 608: 'PH', 616: 'PL', 620: 'PT', 634: 'QA',
  642: 'RO', 643: 'RU', 682: 'SA', 702: 'SG', 704: 'VN', 710: 'ZA', 724: 'ES', 752: 'SE', 756: 'CH',
  760: 'SY', 764: 'TH',  تونس: '', 788: 'TN', 792: 'TR', 804: 'UA', 784: 'AE', 826: 'GB', 840: 'US',
  858: 'UY', 862: 'VE', 887: 'YE'
};

function severityClass(count) {
  if (count >= 6) return 'active-high';
  if (count >= 3) return 'active-mid';
  if (count >= 1) return 'active-low';
  return '';
}

function renderNews(regionName, articles) {
  regionEl.textContent = `${regionName} で起きていること`; 
  newsListEl.innerHTML = '';

  if (!articles || articles.length === 0) {
    newsListEl.innerHTML = '<li class="news-item"><p>この地域に結び付いたニュースはまだありません。</p></li>';
    return;
  }

  for (const article of articles.slice(0, 12)) {
    const li = document.createElement('li');
    li.className = 'news-item';
    li.innerHTML = `
      <span class="badge">${article.source}</span>
      <div><a href="${article.url}" target="_blank" rel="noopener noreferrer">${article.title}</a></div>
      <p>${article.summary}</p>
      <p>${new Date(article.published_at).toLocaleString('ja-JP', { dateStyle: 'medium', timeStyle: 'short' })}</p>
    `;
    newsListEl.appendChild(li);
  }
}

async function bootstrap() {
  const [worldRes, newsRes] = await Promise.all([fetch(WORLD_ATLAS_URL), fetch(NEWS_DATA_URL)]);
  const world = await worldRes.json();
  const newsData = await newsRes.json();

  metaEl.textContent = `更新: ${new Date(newsData.generated_at).toLocaleString('ja-JP', { dateStyle: 'medium', timeStyle: 'short' })} / 件数: ${newsData.articles.length}`;

  const countryMap = new Map(newsData.regions.map((r) => [r.country_code, r]));
  const articlesByCode = new Map();
  for (const article of newsData.articles) {
    if (!articlesByCode.has(article.country_code)) articlesByCode.set(article.country_code, []);
    articlesByCode.get(article.country_code).push(article);
  }

  const countries = topojson.feature(world, world.objects.countries).features;

  svg
    .append('g')
    .selectAll('path')
    .data(countries)
    .join('path')
    .attr('class', (d) => {
      const alpha2 = ISO_NUMERIC_TO_ALPHA2[Number(d.id)];
      const region = alpha2 ? countryMap.get(alpha2) : null;
      const classes = ['country'];
      if (region) classes.push(severityClass(region.news_count));
      return classes.join(' ');
    })
    .attr('d', path)
    .on('click', function (_, d) {
      svg.selectAll('.country').classed('selected', false);
      d3.select(this).classed('selected', true);

      const alpha2 = ISO_NUMERIC_TO_ALPHA2[Number(d.id)];
      const region = alpha2 ? countryMap.get(alpha2) : null;
      const regionName = region?.country_name || d.properties?.name || alpha2 || 'Unknown';
      renderNews(regionName, alpha2 ? articlesByCode.get(alpha2) || [] : []);
    });

  const topRegion = [...newsData.regions].sort((a, b) => b.news_count - a.news_count)[0];
  if (topRegion) {
    renderNews(topRegion.country_name, articlesByCode.get(topRegion.country_code) || []);
  }
}

bootstrap().catch((error) => {
  console.error(error);
  regionEl.textContent = 'データの読み込みに失敗しました。';
  newsListEl.innerHTML = '<li class="news-item"><p>GitHub Actions の生成結果と JSON パスを確認してください。</p></li>';
});
