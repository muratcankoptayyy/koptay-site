import React from "react";
import Financial_carousel from "../carousel/financial_carousel";

const Financialnews = () => {
  return (
    <div>
      {/* <!-- Blog --> */}
      <section className="financial-section bg-light-base py-24 dark:bg-jacarta-900 ">
        <div className="container">
          <div className="mx-auto mb-12 max-w-sm text-center">
            <h2 className="mb-6 text-center font-display text-3xl font-medium text-jacarta-700 dark:text-white">
              Blog & Duyurular
            </h2>
            <p className="text-lg dark:text-jacarta-300">
              TevkilApp ile ilgili en güncel haberleri ve duyuruları buradan takip edebilirsiniz.
            </p>
          </div>

          {/* <!-- Slider --> */}
          <Financial_carousel />
        </div>
      </section>
      {/* <!-- end blog --> */}
    </div>
  );
};

export default Financialnews;
