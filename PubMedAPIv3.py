from Bio import Entrez
import os
import time

Entrez.email = "nitish.salvi@gmail.com"  # Update this with your actual email

def controlled_request(call_function):
    time.sleep(1 / 3)  # Wait for 1/3rd of a second to comply with 3 requests per second limit
    return call_function()

def search_and_fetch_abstracts(topic, subtopic):
    search_query = f"{topic} AND {subtopic}"
    def call_esearch():
        return Entrez.esearch(db='pubmed', term=search_query, retmax='10', retmode='xml')
    handle = controlled_request(call_esearch)
    results = Entrez.read(handle)
    handle.close()

    records = []
    id_list = results['IdList']
    if not id_list:  # Check if id_list is empty
        print(f"No records found for {search_query}")
    else:
        def call_efetch():
            return Entrez.efetch(db='pubmed', id=','.join(id_list), retmode='xml', rettype='abstract')
        handle = controlled_request(call_efetch)
        records = Entrez.read(handle)
        handle.close()
    handle = controlled_request(call_efetch)
    records = Entrez.read(handle)
    print(f"Structure of records: {type(records)}")  # Add this to inspect the structure
    handle.close()
    return records

def save_abstracts_to_files(records, folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    for record in records['PubmedArticle']:
        try:
            pmid = record['MedlineCitation']['PMID']
            title = record['MedlineCitation']['Article']['ArticleTitle']
            if 'Abstract' in record['MedlineCitation']['Article']:
                abstract = record['MedlineCitation']['Article']['Abstract']['AbstractText'][0]
            else:
                abstract = "No abstract available."
            content = f"Title: {title}\nPMID: {pmid}\nAbstract:\n{abstract}\nCitations:\n"
            
            filename = os.path.join(folder_path, f"{pmid}.txt")
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"Saved abstract to {filename}")
        except KeyError as e:
            print("Error processing record {e}, skipping...")
            continue

def main():
    topic = input("Enter main topic: ")
    subtopics = []
    while True:
        subtopic = input("Enter subtopic (type 'done' when finished): ")
        if subtopic.lower() == 'done':
            break
        subtopics.append(subtopic)
    
    for subtopic in subtopics:
        print(f"Processing subtopic: {subtopic}")
        records = search_and_fetch_abstracts(topic, subtopic)
        local_folder_path = os.path.join("PubMed_Abstracts", topic, subtopic)  # Create subtopic specific folder
        save_abstracts_to_files(records, local_folder_path)

if __name__ == "__main__":
    main()
