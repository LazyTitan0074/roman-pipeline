"""Formatare oficiala: incarca proiectul, init client, ruleaza format_book."""
import typer
typer.confirm = lambda *a, **k: True
import libriscribe.main as m
m.typer.confirm = lambda *a, **k: True
from libriscribe.agents.project_manager import ProjectManagerAgent

pm = ProjectManagerAgent(llm_client=None)
pm.load_project_data("leah_si_lara")
pkb = pm.project_knowledge_base
pm.initialize_llm_client(pkb.llm_provider, pkb.model)
print("format client:", pkb.llm_provider, "/", pkb.model)
pm.format_book("manuscript_official.md")
pm.checkpoint()
print("DONE")
