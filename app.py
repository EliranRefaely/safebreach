import pandas as pd
import streamlit as st
from search import Searcher


def main():
    st.title('Yellow Page')
    st.markdown("Please fill the search parameters below and click on the 'Submit' button in order to get the contact details")
    
 
    name = st.text_input('Enter Name:')
    age = st.text_input('Enter Age:')
    phone_number = st.text_input('Enter Phone number:')
    address = st.text_input('Enter Address:')

    if st.button('Submit'):
        with st.spinner('Searching...'):
            filters = {'name': name, 'age': age, 'phone_number': phone_number, 'address': address}
            print(filters)

            searcher = Searcher()
            contacts = searcher.search_contacts(search_criteria=filters)
            if contacts:
                df = pd.DataFrame(contacts)
                df['picture'] = df['picture'].apply(lambda picture: f'./assets/images/{picture}')
                st.dataframe(df)

                st.image(df['picture'].tolist(), width=60)
                st.success('Searching completed successfully!')
            else:
                st.warning('No results found!')

if __name__ == '__main__':
    main()