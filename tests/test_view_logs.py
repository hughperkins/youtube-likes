import datetime
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from youtube_likes_lib import view_logs


NOW = datetime.datetime(2026, 10, 3, 12, tzinfo=datetime.timezone.utc)


class HistoryTests(unittest.TestCase):
    def calculate(self, rows=None, text=None):
        with tempfile.TemporaryDirectory() as folder:
            logfile = Path(folder) / 'history.yaml'
            logfile.write_text(text if text is not None else ''.join(
                '- ' + json.dumps(row) + '\n' for row in rows))
            with patch.object(view_logs.datetime, 'datetime', wraps=datetime.datetime) as clock:
                clock.now.return_value = NOW
                return view_logs.get_delta_stats_many([8, 24, 48], str(logfile), 'test')

    def row(self, hours, views, likes=0):
        return dict(dt=(NOW - datetime.timedelta(hours=hours)).strftime('%Y%m%d-%H%M'),
                    views=views, likes=likes)

    def test_matches_sorted_reference(self):
        rows = [self.row(h, 10000 - h * h, 1000 - h * 2) for h in range(70, -1, -3)]
        actual = self.calculate(rows)
        for hours, result in actual.items():
            baseline = min(rows, key=lambda r: abs(
                (NOW.replace(tzinfo=None) - datetime.datetime.strptime(r['dt'], '%Y%m%d-%H%M'))
                .total_seconds() / 3600 - hours))
            elapsed = (datetime.datetime.strptime(rows[-1]['dt'], '%Y%m%d-%H%M') -
                       datetime.datetime.strptime(baseline['dt'], '%Y%m%d-%H%M')).total_seconds() / 3600
            self.assertEqual(result.d_views, int((rows[-1]['views'] - baseline['views']) * hours / elapsed))
            self.assertEqual(result.d_likes, int((rows[-1]['likes'] - baseline['likes']) * hours / elapsed))

    def test_cutoff_and_empty_history(self):
        for rows in [[], [self.row(73, 10)], [self.row(73, 10), self.row(0, 100)]]:
            self.assertTrue(all(r.d_views == 0 for r in self.calculate(rows).values()))

    def test_first_entry_wins_tie(self):
        result = self.calculate([self.row(9, 10), self.row(7, 80), self.row(0, 100)])
        self.assertEqual(result[8].d_views, 80)

    def test_legacy_yaml_and_comments(self):
        rows = [self.row(48, 10), self.row(0, 100)]
        from ruamel.yaml import YAML
        import io
        stream = io.StringIO()
        YAML().dump(rows, stream)
        self.assertEqual(self.calculate(rows), self.calculate(text=stream.getvalue()))
        text = '# comment\n\n' + ''.join('- ' + json.dumps(r) + '\n' for r in rows)
        self.assertEqual(self.calculate(rows), self.calculate(text=text))

    def test_missing_counts_default_to_zero(self):
        result = self.calculate([{'dt': self.row(48, 0)['dt']}, self.row(0, 100)])
        self.assertEqual(result[48].d_views, 100)


if __name__ == '__main__':
    unittest.main()
