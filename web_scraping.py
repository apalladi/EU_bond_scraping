from src.scraping import extract_multiple_ISIN

if __name__ == "__main__":
    path = "https://www.simpletoolsforinvestors.eu/data/listino/listino.csv"
    data = pd.read_csv(path, sep=";")
    data = data[data["Currency"] == "EUR"]
    list_ISIN = np.unique(np.array(data["ISIN Code"]))
    print("Number of ISIN", len(list_ISIN))
    
    df = extract_multiple_ISIN(list_ISIN)
    
    os.makedirs("results", exist_ok=True)
    df.to_csv("results/bond_info_extracted.csv")
