pred_design_html = """
<body>
<form action="/predict/" enctype="multipart/form-data" method="post">
<input name="file" type="file" multiple>
<input type="submit">
</form>
</body>
    """
query_design_html = f"""
            <html>
            <body>

            <h1>GalaxEye Analyst Query</h1>

            <form action="/result" method="get">
                <label>Predicted Class:</label>

                <select name="predicted_cls">

                    <option value="AnnualCrop">
                        AnnualCrop
                    </option>

                    <option value="Forest">
                        Forest
                    </option>

                    <option value="Highway">
                        Highway
                    </option>

                    <option value="Industrial">
                        Industrial
                    </option>

                    <option value="Residential">
                        Residential
                    </option>

                    <option value="River">
                        River
                    </option>

                    <option value="SeaLake">
                        SeaLake
                    </option>


            </select>

                <br><br>

                <label>Min Confidence:</label>
                <input
                    name="min_confidence"
                    type="number"
                    step="0.01"
                    min="0"
                    max="1"
                    value="0.1"
                >
                <br><br>

                <label>Max Confidence:</label>
                <input
                    name="max_confidence"
                    type="number"
                    step="0.01"
                    min="0"
                    max="1"
                    value="0.5"
                >
                <br><br>

                <label>Need Review:</label>

                <select name="need_review">

                    <option value="false">
                        No
                    </option>

                    <option value="true">
                        Yes
                    </option>

                </select>

                <br><br>

                <label>Review Status:</label>

                <select name="review_status">

                    <option value="0">
                        None
                    </option>

                    <option value="pending">
                        Pending
                    </option>

                    <option value="reviewed">
                        Reviewed
                    </option>


                </select>

                <br><br>

                <label>Model Version:</label>

                <input
                    name="model_version"
                    type="text"
                    value="model_v0.0"
                >

                <br><br>

                <input
                    type="submit"
                    value="Run Query"
                >

            </form>

            </body>
            </html>
            """
