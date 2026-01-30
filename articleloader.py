from langchain_community.document_loaders import WebBaseLoader
def load_article(url):
    loader=WebBaseLoader(url,requests_kwargs={"timeout": 30})
    return loader.load()