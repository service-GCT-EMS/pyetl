
new Vue({
    el: "#app",

    data() {
        return {
            question: '',
            answer: 'Questions usually contain a question mark. ;-)',
            jobTitles: [
                { name: "Product designer", id: 1 },
                { name: "Full-stack developer", id: 2 },
                { name: "Product manager", id: 3 },
                { name: "Senior front-end developer", id: 4 }
            ],
            selectedJobTitle: null,
            essai2: ["aaaa", "bbbb", "cccc"]
        }
    },
    watch: {
        // whenever question changes, this function will run
        question(newQuestion, oldQuestion) {
            if (newQuestion.indexOf('?') > -1) {
                this.getAnswer()
            }

        },

    },
    methods: {
        getAnswer() {
            this.answer = 'Thinking...'
            axios
                .get('https://yesno.wtf/api')
                .then(response => {
                    this.answer = response.data.answer
                })
                .catch(error => {
                    this.answer = 'Error! Could not reach the API. ' + error
                })
        },
        getvalues()
        changeJobTitle(event) {
            this.selectedJobTitle = event.target.options[event.target.options.selectedIndex].text
            this.essai2 = axios.get(http://127.0.0.1:5000/mws/params))
                this.essai2 = [this.selectedJobTitle, this.selectedJobTitle, this.selectedJobTitle]
        }




    }
})
