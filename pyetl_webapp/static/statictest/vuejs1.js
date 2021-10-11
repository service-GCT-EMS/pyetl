new Vue({
    el: "#app",
    data: function () {
        url = 'http://127.0.0.1:5000/mws/params'
        params = {
            clef: 'server',
            val: 'host=bdsigli.cus.fr port=34000'
        }
        axios.post(url, {}, { params }
        )
            .then(response => {
                return success(response);
            })
            .catch(error => {
                return fail(error);
            });
    }
})
