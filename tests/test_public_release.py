"""Standard-library portable release tests; no site/network access."""
from pathlib import Path
import re, subprocess, sys, unittest, json, hashlib
ROOT = Path(__file__).resolve().parents[1]
SKILLS = sorted((ROOT/'skills').glob('yalda-motion-*'))

class ReleaseTests(unittest.TestCase):
    def test_two_independent_skills(self):
        self.assertEqual([p.name for p in SKILLS],['yalda-motion-auditor','yalda-motion-designer'])

    def test_standard_frontmatter(self):
        for p in SKILLS:
            text=(p/'SKILL.md').read_text(encoding='utf-8')
            self.assertTrue(text.startswith('---\n'))
            head=text.split('---\n',2)[1]
            m=re.search(r'(?m)^name:\s*([^\n]+)$',head)
            self.assertIsNotNone(m)
            self.assertEqual(m.group(1).strip(),p.name)
            self.assertRegex(p.name,r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
            self.assertLessEqual(len(p.name),64)
            d=re.search(r'(?m)^description:\s*(.+)$',head)
            self.assertIsNotNone(d)
            self.assertGreater(len(d.group(1).strip()),30)
            self.assertLessEqual(len(d.group(1)),1024)
            self.assertLessEqual(len(text.splitlines()),500)
            self.assertIn('0.5.0',text)

    def test_references_exist(self):
        for p in SKILLS:
            text=(p/'SKILL.md').read_text(encoding='utf-8')
            links=re.findall(r'\]\((references/[^)]+)\)',text)
            self.assertGreaterEqual(len(links),6)
            for link in links:
                self.assertTrue((p/link).is_file(),(p.name,link))

    def test_agents_metadata_consistency(self):
        for p in SKILLS:
            text=(p/'agents/openai.yaml').read_text(encoding='utf-8')
            self.assertIn('YALDA Motion '+p.name.split('-')[-1].title(),text)
            self.assertIn('default_prompt:',text)

    def test_no_private_runtime_or_generated_code(self):
        banned=('__pycache__','.pyc','.pyo','.DS_Store','.pem','.key','.env')
        for p in (ROOT/'skills').rglob('*'):
            if p.is_file():
                self.assertFalse(p.name.endswith(banned),str(p))
                self.assertNotIn('staging.yaldaeng.ir',p.read_text(encoding='utf-8',errors='ignore'),str(p))
        self.assertFalse(any((ROOT/'skills').rglob('*.zip')))

    def test_python_syntax(self):
        for p in ROOT.glob('skills/*/scripts/*.py'):
            compile(p.read_bytes(),str(p),'exec')

    def test_python_tools_help(self):
        for p in ROOT.glob('skills/*/scripts/*.py'):
            with self.subTest(p=str(p.relative_to(ROOT))):
                r=subprocess.run([sys.executable,str(p),'--help'],capture_output=True,text=True,timeout=10)
                self.assertEqual(r.returncode,0,(p.name,r.stderr[-500:]))

    def test_sample_timeline_validation(self):
        for p in SKILLS:
            example=p/'assets/r4-visual-timeline-EXAMPLE-NOT-OWNER-APPROVED.json'
            tool=p/'scripts/validate_visual_timeline.py'
            r=subprocess.run([sys.executable,str(tool),str(example)],capture_output=True,text=True,timeout=10)
            self.assertEqual(r.returncode,0,r.stderr)
            obj=json.loads(r.stdout)
            self.assertTrue(obj['status'].startswith('STRUCTURAL_PASS'),obj)
            self.assertEqual(obj['errors'],[])

    def test_synthetic_momentum_and_caption_scripts(self):
        for p in SKILLS:
            for name,fixture in [('audit_scroll_momentum.py','r4-motion-sample-SYNTHETIC.jsonl'),('audit_caption_coverage.py','caption-coverage-SYNTHETIC.jsonl')]:
                r=subprocess.run([sys.executable,str(p/'scripts'/name),str(p/'assets'/fixture)],capture_output=True,text=True,timeout=10)
                self.assertEqual(r.returncode,0,r.stderr)
                out=json.loads(r.stdout)
                self.assertIn('status',out)
                self.assertNotIn('VISUAL_PASS',out['status'])

    def test_site_article_and_publication_gate(self):
        md=(ROOT/'docs/article-fa.md').read_text(encoding='utf-8')
        html=(ROOT/'docs/article-fa.html').read_text(encoding='utf-8')
        checklist=(ROOT/'PUBLICATION_CHECKLIST.md').read_text(encoding='utf-8')
        self.assertGreater(len(md),5000)
        self.assertIn('lang="fa" dir="rtl"',html)
        self.assertIn('Owner approved Apache License 2.0', checklist)
        self.assertTrue((ROOT/'LICENSE').is_file())
if __name__=='__main__':unittest.main()
