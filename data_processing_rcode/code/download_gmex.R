# Visit the [Gulf of Mexico]("https://seamap.gsmfc.org/") website
# Click "Download" the SEAMAP Trawl/Plankton, Bottom Longline
# Fill in the form ("Scientific Research", "Educational Institution", "Trawl/Plankton Data (CSV)"
# Unzip the CSV in your downloads folder
# then copy them into the data_raw folder with the script below

file.copy(from = "C:/Users/Melissa.Karp//Downloads/public_seamap_csvs/public_seamap_csvs/BGSREC.csv", to = "C:/Users/Melissa.Karp/Documents/transfer/DisMAP project/DisMAP/data_processing_rcode/data/gmex_BGSREC.csv", overwrite = T)
file.copy(from = "C:/Users/Melissa.Karp//Downloads/public_seamap_csvs/public_seamap_csvs/CRUISES.csv", to = "C:/Users/Melissa.Karp/Documents/transfer/DisMAP project/DisMAP/data_processing_rcode/data/gmex_CRUISES.csv", overwrite = T)
file.copy(from = "C:/Users/Melissa.Karp//Downloads/public_seamap_csvs/public_seamap_csvs/STAREC.csv", to = "C:/Users/Melissa.Karp/Documents/transfer/DisMAP project/DisMAP/data_processing_rcode/data/gmex_STAREC.csv", overwrite = T)
file.copy(from = "C:/Users/Melissa.Karp//Downloads/public_seamap_csvs/public_seamap_csvs/INVREC.csv", to = "C:/Users/Melissa.Karp/Documents/transfer/DisMAP project/DisMAP/data_processing_rcode/data/gmex_INVREC.csv", overwrite = T)
#file.copy(from = "C:/Users/Melissa.Karp//Downloads/public_seamap_csvs/public_seamap_csvs/NEWBIOCODESBIG.csv", to = "C:/Users/Melissa.Karp/Documents/transfer/DisMAP project/DisMAP/data_processing_rcode/data_raw/gmex_NEWBIOCODESBIG_2024.csv", overwrite = T)
#Note: for the updated BioCodes table need to reach out to David Hanisko at the SEFSC