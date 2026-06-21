const fs = require('fs');

const path = 'public/data/theme_cooccurrence.json';
const data = JSON.parse(fs.readFileSync(path, 'utf-8'));

const total_scripts = 1473;
const topic_totals = data.topic_totals;
const cooc = data.cooc_matrix;

const assoc_rules = [];
const theme_names = Object.keys(topic_totals);

for (const t1 of theme_names) {
  for (const t2 of theme_names) {
    if (t1 === t2) continue;
    const co_count = cooc[t1][t2] || 0;
    if (co_count < 3) continue;
    
    const support = co_count / total_scripts;
    const confidence = topic_totals[t1] > 0 ? co_count / topic_totals[t1] : 0;
    const base_prob = topic_totals[t2] / total_scripts;
    const lift = base_prob > 0 ? confidence / base_prob : 0;
    
    assoc_rules.push({
      antecedent: t1,
      consequent: t2,
      support: support,
      confidence: confidence,
      lift: lift
    });
  }
}

// 按照 Lift (提升度) 降序排序，取前 30 名
assoc_rules.sort((a, b) => b.lift - a.lift);
data.association_rules = assoc_rules.slice(0, 30);

fs.writeFileSync(path, JSON.stringify(data, null, 2));
console.log('Fixed association_rules with lowered lift threshold!');
