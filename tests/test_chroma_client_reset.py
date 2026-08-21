from types import SimpleNamespace

import app.retrieval.chroma_client as chroma_client


def test_chroma_client_recovers_from_corrupt_collection_metadata(monkeypatch, tmp_path):
    chroma_client.ChromaDBClient._instance = None
    monkeypatch.setattr(
        chroma_client,
        "settings",
        SimpleNamespace(chroma_path=str(tmp_path / "chroma"), collection_name="test_collection"),
    )

    attempts = {"count": 0}

    class FakeClient:
        def __init__(self, path, settings):
            self.path = path
            self.settings = settings

        def get_or_create_collection(self, name, metadata=None):
            attempts["count"] += 1
            if attempts["count"] == 1:
                raise KeyError("_type")
            return object()

    monkeypatch.setattr(chroma_client.chromadb, "PersistentClient", FakeClient)

    client = chroma_client.ChromaDBClient()

    assert client is not None
    assert attempts["count"] == 2
