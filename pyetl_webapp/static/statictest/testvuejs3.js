
new Vue({
    el: "#app",
    data() {
        return {
            jobTitles: [
                { name: "Product designer", id: 1 },
                { name: "Full-stack developer", id: 2 },
                { name: "Product manager", id: 3 },
                { name: "Senior front-end developer", id: 4 }
            ],
            nrep: 1,
            selectedJobTitle: "test",
            essai2: [],
            params: { n: this.nrep, valeur: "toto" },
            url: "http://127.0.0.1:5000/mws/fakelist1",
        }
    },

    watch: {
        // whenever nrep changes, this function will run
        nrep(newNrep, oldNrep) {
            this.params.n = newNrep
            this.getValues(this.url, this.params)
        }

    },



    methods: {
        getValues(url, params) {
            axios
                .get(url, { params })
                .then(response => {
                    this.essai2 = response.data
                })
                .catch(error => {
                    this.essai2 = 'Error! Could not reach the API. ' + error
                })
        },


        changeJobTitle(event) {
            this.selectedJobTitle = event.target.options[event.target.options.selectedIndex].text
            //this.getValues()
            this.params.valeur = this.selectedJobTitle
            this.getValues(this.url, this.params)

        }




    }
})
