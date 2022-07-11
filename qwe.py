for j, _function in enumerate(_functions):
    new_vals=[None]*n_obs
    new_links=[None]*n_obs
    converteds=[None]*n_obs

    col=_function.__name__.replace("_", "")
    col_link=f"{col}_link"

    old_val=df.loc[i, col]

    if not pd.isna(old_val):
        new_vals[i]=old_val
        converted=True

        print(f"{i}/{tot} - {surname} - {col} - already done")

    elif pd.isna(old_val):

        try:
            new_val, new_link=_function(surname)
            new_vals[i]=new_val
            new_links[i]=new_link
            converted=True

            print(f"{i}/{tot} - {surname} - {col} - done")

        except Exception as e:
            new_vals[i]=pd.NA
            new_links[i]=pd.NA
            converted=False

            print(f"{i}/{tot} - {surname} - {col} - error")
            print(e)
            
        time.sleep(time_sleep)

        converteds[i]=converted

    df[col]=new_vals
    df[col_link]=new_links
    df[f"{col}_converted"]=converteds