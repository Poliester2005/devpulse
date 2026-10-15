"""Testes offline (sem rede) das partes de parsing e renderização."""
import unittest

from devpulse import notifiers, report
from devpulse.models import Item, Section
from devpulse.sources import markets, trending


class MarketsTest(unittest.TestCase):
    def test_parse_formata_preco_e_variacao(self):
        data = {"USDBRL": {"bid": "5.4321", "pctChange": "-0.35"},
                "BTCBRL": {"bid": "350123.9", "pctChange": "1.2"}}
        items = markets.parse(data)
        self.assertEqual(items[0].text, "Dólar: R$ 5,43")
        self.assertIn("▼", items[0].detail)
        self.assertEqual(items[1].text, "Bitcoin: R$ 350.123,90")


class TrendingTest(unittest.TestCase):
    HTML = """<article class="Box-row"><h2><a href="/user/repo"> user / repo </a></h2>
    <p> Uma lib   legal </p><span class="d-inline-block float-sm-right">123 stars today</span></article>"""

    def test_parse_extrai_campos(self):
        item = trending.parse(self.HTML, 5)[0]
        self.assertEqual(item.text, "user/repo: Uma lib legal")
        self.assertEqual(item.url, "https://github.com/user/repo")
        self.assertEqual(item.detail, "123 stars today")


class ReportTest(unittest.TestCase):
    def test_escapa_html_e_mostra_erro(self):
        sections = [Section("Teste", "🧪", [Item("<script>x</script>", "https://a.b")]),
                    Section("Quebrada", "💥", error="timeout")]
        text = report.render_telegram(sections)
        self.assertNotIn("<script>", text)
        self.assertIn("indisponível: timeout", text)

    def test_chunks_respeitam_limite(self):
        text = "\n\n".join("x" * 1500 for _ in range(5))
        self.assertTrue(all(len(c) <= 4000 for c in notifiers._chunks(text)))


if __name__ == "__main__":
    unittest.main()
