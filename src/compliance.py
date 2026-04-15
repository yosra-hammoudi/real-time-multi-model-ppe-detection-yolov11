def check_epi_compliance(nb_persons, epi_counts, required_epis):
    alerts = []
    
    if nb_persons >= 1:
        for epi in required_epis:
            epi_count = epi_counts.get(epi, 0)
            
            if epi_count < (nb_persons - 1):
                epi_name = epi.replace("-", " ").capitalize()
                missing_count = nb_persons - epi_count
                alerts.append(f"{missing_count} personne(s) sans {epi_name}")
    
    if alerts:
        return "⚠️ ALERTE : " + " | ".join(alerts)
    
    return None